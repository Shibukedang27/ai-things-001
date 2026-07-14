from sqlalchemy.orm import Session

from backend.exceptions import AuthenticationError, ConflictError
from backend.models.permission import Permission
from backend.models.role import Role
from backend.models.user import User
from backend.repositories.permission_repository import PermissionRepository
from backend.repositories.role_repository import RoleRepository
from backend.repositories.user_repository import UserRepository
from backend.schemas.auth import TokenPair
from backend.schemas.user import UserCreate
from backend.security.jwt import TokenType, create_token_pair, decode_token
from backend.security.password import hash_password, verify_password
from backend.services.access_control import SYSTEM_PERMISSIONS, SYSTEM_ROLES
from backend.utils.datetime import utc_now


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.roles = RoleRepository(session)
        self.permissions = PermissionRepository(session)

    def register_user(self, payload: UserCreate) -> User:
        existing_user = self.users.get_by_email(payload.email)
        if existing_user:
            raise ConflictError("A user with this email already exists.")

        self.ensure_access_model()
        role_name = "owner" if self.users.total_users() == 0 else "researcher"
        role = self.roles.get_by_name(role_name)
        if role is None:
            raise AuthenticationError("Access control could not be initialized.")

        user = User(
            email=payload.email.lower(),
            full_name=payload.full_name,
            hashed_password=hash_password(payload.password.get_secret_value()),
            is_active=True,
            is_verified=False,
            roles=[role],
        )
        self.users.add(user)
        self.session.commit()
        registered_user = self.users.get_with_roles(user.id)
        if registered_user is None:
            raise AuthenticationError("Registered user could not be loaded.")
        return registered_user

    def authenticate_user(self, email: str, password: str) -> User:
        user = self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password.")
        if not user.is_active:
            raise AuthenticationError("This account is inactive.")
        user.last_login_at = utc_now()
        self.session.commit()
        loaded_user = self.users.get_with_roles(user.id)
        if loaded_user is None:
            raise AuthenticationError("Authenticated user could not be loaded.")
        return loaded_user

    def issue_tokens(self, user: User) -> TokenPair:
        access_token, refresh_token, expires_in = create_token_pair(
            subject=user.id,
            roles=[role.name for role in user.roles],
            permissions=sorted(
                {
                    permission.name
                    for role in user.roles
                    for permission in role.permissions
                }
            ),
        )
        return TokenPair(access_token=access_token, refresh_token=refresh_token, expires_in=expires_in)

    def refresh_tokens(self, refresh_token: str) -> TokenPair:
        payload = decode_token(refresh_token, expected_type=TokenType.REFRESH)
        user = self.users.get_with_roles(payload.subject)
        if user is None or not user.is_active:
            raise AuthenticationError("Refresh token subject is invalid.")
        return self.issue_tokens(user)

    def ensure_access_model(self) -> None:
        permission_lookup: dict[str, Permission] = {}
        for definition in SYSTEM_PERMISSIONS:
            permission = self.permissions.get_by_name(definition.name)
            if permission is None:
                permission = Permission(
                    name=definition.name,
                    resource=definition.resource,
                    action=definition.action,
                    description=definition.description,
                )
                self.permissions.add(permission)
            permission_lookup[definition.name] = permission

        for role_name, role_definition in SYSTEM_ROLES.items():
            role = self.roles.get_by_name(role_name)
            if role is None:
                role = Role(
                    name=role_name,
                    description=str(role_definition["description"]),
                    is_system=True,
                )
                self.roles.add(role)
            permission_names = tuple(role_definition["permissions"])
            role.permissions = [permission_lookup[name] for name in permission_names]

        self.session.flush()
