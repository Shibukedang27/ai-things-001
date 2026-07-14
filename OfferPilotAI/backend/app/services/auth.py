"""Authentication service."""

from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Environment, Settings
from app.core.exceptions import AuthenticationError, AuthorizationError, ConflictError, NotFoundError
from app.domain.enums import SessionStatus
from app.models import Session, User
from app.repositories import (
    AuthCredentialRepository,
    PasswordResetTokenRepository,
    RefreshTokenRepository,
    RoleRepository,
    SessionRepository,
    UserRepository,
    UserRoleRepository,
)
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordResponse,
    LoginRequest,
    ProfileUpdateRequest,
    RoleCreate,
    RoleRead,
    SessionSummary,
    SignupRequest,
    TokenPair,
    UserProfile,
)
from app.utils.ids import create_id
from app.utils.security import (
    create_jti,
    create_jwt,
    create_opaque_token,
    create_token_fingerprint,
    decode_jwt,
    hash_password,
    password_needs_rehash,
    validate_password_strength,
    verify_password,
)
from app.utils.time import utc_now


@dataclass(frozen=True)
class AuthenticatedPrincipal:
    """Authenticated user context."""

    user: User
    roles: list[str]
    access_jti: str


class AuthService:
    """Authentication and authorization workflows."""

    def __init__(self, session: AsyncSession, settings: Settings) -> None:
        self.session = session
        self.settings = settings
        self.users = UserRepository(session)
        self.credentials = AuthCredentialRepository(session)
        self.roles = RoleRepository(session)
        self.user_roles = UserRoleRepository(session)
        self.sessions = SessionRepository(session)
        self.refresh_tokens = RefreshTokenRepository(session)
        self.password_resets = PasswordResetTokenRepository(session)

    async def signup(
        self,
        payload: SignupRequest,
        *,
        ip_address: str | None,
        user_agent: str | None,
    ) -> AuthResponse:
        validate_password_strength(payload.password, email=str(payload.email))
        existing_user = await self.users.get_by_email(str(payload.email).lower())
        if existing_user:
            raise ConflictError("A user with this email already exists.")

        try:
            user = await self.users.create(
                {
                    "email": str(payload.email).lower(),
                    "full_name": payload.full_name,
                    "is_active": True,
                    "is_verified": False,
                }
            )
            await self.credentials.create(
                {
                    "user_id": user.id,
                    "password_hash": hash_password(payload.password),
                    "password_changed_at": utc_now(),
                }
            )
            default_role = await self._ensure_role(
                name="user",
                description="Standard OfferPilot AI user",
                permissions=["profile:read", "profile:update", "interviews:manage"],
                is_system=True,
            )
            await self.user_roles.create({"user_id": user.id, "role_id": default_role.id})
            tokens = await self._issue_token_pair(user=user, ip_address=ip_address, user_agent=user_agent)
            await self.session.commit()
            await self.session.refresh(user)
            return AuthResponse(user=await self.build_user_profile(user), tokens=tokens)
        except IntegrityError as exc:
            await self.session.rollback()
            raise ConflictError("Signup could not be completed because of a database constraint.") from exc

    async def login(
        self,
        payload: LoginRequest,
        *,
        ip_address: str | None,
        user_agent: str | None,
    ) -> AuthResponse:
        user = await self.users.get_by_email(str(payload.email).lower())
        if not user:
            raise AuthenticationError("Invalid email or password.")
        if not user.is_active:
            raise AuthenticationError("User account is inactive.")

        credential = await self.credentials.get_by_user_id(user.id)
        if not credential:
            raise AuthenticationError("Invalid email or password.")

        now = utc_now()
        if credential.locked_until and credential.locked_until > now:
            raise AuthenticationError("User account is temporarily locked.")

        if not verify_password(payload.password, credential.password_hash):
            credential.failed_login_attempts += 1
            if credential.failed_login_attempts >= self.settings.max_login_attempts:
                credential.locked_until = now + timedelta(minutes=self.settings.account_lock_minutes)
            await self.session.commit()
            raise AuthenticationError("Invalid email or password.")

        if password_needs_rehash(credential.password_hash):
            credential.password_hash = hash_password(payload.password)

        credential.failed_login_attempts = 0
        credential.locked_until = None
        credential.last_login_at = now
        tokens = await self._issue_token_pair(user=user, ip_address=ip_address, user_agent=user_agent)
        await self.session.commit()
        await self.session.refresh(user)
        return AuthResponse(user=await self.build_user_profile(user), tokens=tokens)

    async def refresh(self, refresh_token: str, *, ip_address: str | None, user_agent: str | None) -> TokenPair:
        payload = decode_jwt(refresh_token, settings=self.settings, expected_type="refresh")
        token_hash = create_token_fingerprint(refresh_token)
        token_record = await self.refresh_tokens.get_by_jti_and_hash(jti=payload["jti"], token_hash=token_hash)
        now = utc_now()

        if not token_record or token_record.revoked_at or token_record.expires_at <= now:
            raise AuthenticationError("Invalid refresh token.")

        user = await self.users.get(token_record.user_id)
        if not user or not user.is_active:
            raise AuthenticationError("Invalid refresh token.")

        session_record = await self.sessions.get(token_record.session_id)
        if not session_record or session_record.status != SessionStatus.ACTIVE.value:
            raise AuthenticationError("Invalid refresh token.")

        token_record.revoked_at = now
        new_tokens = await self._rotate_token_pair(
            user=user,
            session_record=session_record,
            previous_refresh_token=token_record,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        await self.session.commit()
        return new_tokens

    async def logout(
        self,
        *,
        principal: AuthenticatedPrincipal,
        refresh_token: str | None,
    ) -> None:
        now = utc_now()
        session_record = await self._get_session_by_access_jti(principal.access_jti)
        if session_record:
            session_record.status = SessionStatus.REVOKED.value
            session_record.revoked_at = now
            await self._revoke_refresh_tokens_for_session(session_record.id, now=now)

        if refresh_token:
            try:
                payload = decode_jwt(refresh_token, settings=self.settings, expected_type="refresh")
            except AuthenticationError:
                payload = None
            if payload:
                token_record = await self.refresh_tokens.get_by_jti(payload["jti"])
                if token_record:
                    token_record.revoked_at = now

        await self.session.commit()

    async def forgot_password(
        self,
        email: str,
        *,
        ip_address: str | None,
        user_agent: str | None,
    ) -> ForgotPasswordResponse:
        user = await self.users.get_by_email(email.lower())
        message = "If the email exists, password reset instructions have been generated."

        if not user or not user.is_active:
            return ForgotPasswordResponse(message=message)

        raw_token = create_opaque_token()
        expires_at = utc_now() + timedelta(minutes=self.settings.password_reset_token_expire_minutes)
        await self.password_resets.create(
            {
                "user_id": user.id,
                "token_hash": create_token_fingerprint(raw_token),
                "expires_at": expires_at,
                "requested_ip": ip_address,
                "user_agent": user_agent,
            }
        )
        await self.session.commit()

        if self.settings.environment == Environment.PRODUCTION:
            return ForgotPasswordResponse(message=message)

        return ForgotPasswordResponse(message=message, reset_token=raw_token, expires_at=expires_at)

    async def reset_password(self, *, token: str, new_password: str) -> None:
        validate_password_strength(new_password)
        now = utc_now()
        reset_record = await self.password_resets.get_usable_by_hash(
            token_hash=create_token_fingerprint(token),
            now=now,
        )
        if not reset_record:
            raise AuthenticationError("Invalid or expired password reset token.")

        credential = await self.credentials.get_by_user_id(reset_record.user_id)
        if not credential:
            raise AuthenticationError("Invalid or expired password reset token.")

        credential.password_hash = hash_password(new_password)
        credential.password_changed_at = now
        credential.failed_login_attempts = 0
        credential.locked_until = None
        reset_record.used_at = now

        await self._revoke_all_user_sessions(reset_record.user_id, now=now)
        await self.session.commit()

    async def build_user_profile(self, user: User) -> UserProfile:
        roles = await self.roles.list_by_user_id(user.id)
        return UserProfile(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_verified=user.is_verified,
            roles=[role.name for role in roles],
            created_at=user.created_at,
            updated_at=user.updated_at,
        )

    async def update_profile(self, principal: AuthenticatedPrincipal, payload: ProfileUpdateRequest) -> UserProfile:
        values = payload.model_dump(exclude_unset=True)
        if values:
            await self.users.update(principal.user, values)
            await self.session.commit()
            await self.session.refresh(principal.user)
        return await self.build_user_profile(principal.user)

    async def list_roles(self) -> list[RoleRead]:
        roles, _ = await self._list_roles()
        return [RoleRead.model_validate(role) for role in roles]

    async def create_role(self, payload: RoleCreate) -> RoleRead:
        existing = await self.roles.get_by_name(payload.name)
        if existing:
            raise ConflictError("Role already exists.")
        role = await self.roles.create(payload.model_dump())
        await self.session.commit()
        await self.session.refresh(role)
        return RoleRead.model_validate(role)

    async def assign_role(
        self,
        *,
        user_id: str,
        role_name: str,
        assigned_by_user_id: str | None,
    ) -> UserProfile:
        user = await self.users.get(user_id)
        if not user:
            raise NotFoundError("User not found.")
        role = await self.roles.get_by_name(role_name)
        if not role:
            raise NotFoundError("Role not found.")
        existing = await self.user_roles.get_assignment(user_id=user.id, role_id=role.id)
        if not existing:
            await self.user_roles.create(
                {
                    "user_id": user.id,
                    "role_id": role.id,
                    "assigned_by_user_id": assigned_by_user_id,
                }
            )
            await self.session.commit()
        return await self.build_user_profile(user)

    async def remove_role(self, *, user_id: str, role_name: str) -> UserProfile:
        user = await self.users.get(user_id)
        if not user:
            raise NotFoundError("User not found.")
        role = await self.roles.get_by_name(role_name)
        if not role:
            raise NotFoundError("Role not found.")
        assignment = await self.user_roles.get_assignment(user_id=user.id, role_id=role.id)
        if assignment:
            await self.user_roles.delete(assignment)
            await self.session.commit()
        return await self.build_user_profile(user)

    async def list_sessions(self, principal: AuthenticatedPrincipal) -> list[SessionSummary]:
        result = await self.session.execute(
            select(Session)
            .where(Session.user_id == principal.user.id)
            .order_by(Session.created_at.desc())
        )
        return [SessionSummary.model_validate(session) for session in result.scalars().all()]

    async def revoke_session(self, *, principal: AuthenticatedPrincipal, session_id: str) -> None:
        session_record = await self.sessions.get(session_id)
        if not session_record:
            raise NotFoundError("Session not found.")
        if session_record.user_id != principal.user.id and "admin" not in principal.roles:
            raise AuthorizationError("You are not allowed to revoke this session.")
        now = utc_now()
        session_record.status = SessionStatus.REVOKED.value
        session_record.revoked_at = now
        await self._revoke_refresh_tokens_for_session(session_record.id, now=now)
        await self.session.commit()

    async def authenticate_access_token(self, token: str) -> AuthenticatedPrincipal:
        payload = decode_jwt(token, settings=self.settings, expected_type="access")
        user = await self.users.get(payload["sub"])
        if not user or not user.is_active:
            raise AuthenticationError("Invalid authentication token.")
        roles = await self.roles.list_by_user_id(user.id)
        return AuthenticatedPrincipal(
            user=user,
            roles=[role.name for role in roles],
            access_jti=payload["jti"],
        )

    async def _issue_token_pair(
        self,
        *,
        user: User,
        ip_address: str | None,
        user_agent: str | None,
    ) -> TokenPair:
        access_token, access_expires_at, access_jti = await self._create_access_token(user)
        session_id = create_id()
        refresh_token, refresh_expires_at, refresh_jti = self._create_refresh_token(user, session_id=session_id)
        await self.sessions.create(
            {
                "id": session_id,
                "user_id": user.id,
                "token_jti": access_jti,
                "status": SessionStatus.ACTIVE.value,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "expires_at": refresh_expires_at,
            }
        )
        await self.refresh_tokens.create(
            {
                "user_id": user.id,
                "session_id": session_id,
                "jti": refresh_jti,
                "token_hash": create_token_fingerprint(refresh_token),
                "expires_at": refresh_expires_at,
                "ip_address": ip_address,
                "user_agent": user_agent,
            }
        )
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int((access_expires_at - utc_now()).total_seconds()),
            refresh_expires_at=refresh_expires_at,
        )

    async def _rotate_token_pair(
        self,
        *,
        user: User,
        session_record: Session,
        previous_refresh_token,
        ip_address: str | None,
        user_agent: str | None,
    ) -> TokenPair:
        access_token, access_expires_at, access_jti = await self._create_access_token(user)
        refresh_token, refresh_expires_at, refresh_jti = self._create_refresh_token(user, session_id=session_record.id)
        previous_refresh_token.replaced_by_jti = refresh_jti
        session_record.token_jti = access_jti
        session_record.expires_at = refresh_expires_at
        session_record.ip_address = ip_address or session_record.ip_address
        session_record.user_agent = user_agent or session_record.user_agent
        await self.refresh_tokens.create(
            {
                "user_id": user.id,
                "session_id": session_record.id,
                "jti": refresh_jti,
                "token_hash": create_token_fingerprint(refresh_token),
                "expires_at": refresh_expires_at,
                "ip_address": ip_address,
                "user_agent": user_agent,
            }
        )
        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int((access_expires_at - utc_now()).total_seconds()),
            refresh_expires_at=refresh_expires_at,
        )

    async def _create_access_token(self, user: User) -> tuple[str, object, str]:
        roles = await self.roles.list_by_user_id(user.id)
        return create_jwt(
            subject=user.id,
            token_type="access",
            settings=self.settings,
            expires_delta=timedelta(minutes=self.settings.access_token_expire_minutes),
            extra_claims={"roles": [role.name for role in roles]},
        )

    def _create_refresh_token(self, user: User, *, session_id: str) -> tuple[str, object, str]:
        return create_jwt(
            subject=user.id,
            token_type="refresh",
            settings=self.settings,
            expires_delta=timedelta(days=self.settings.refresh_token_expire_days),
            jti=create_jti(),
            extra_claims={"session_id": session_id},
        )

    async def _ensure_role(self, *, name: str, description: str, permissions: list[str], is_system: bool):
        role = await self.roles.get_by_name(name)
        if role:
            return role
        return await self.roles.create(
            {
                "name": name,
                "description": description,
                "permissions": permissions,
                "is_system": is_system,
            }
        )

    async def _list_roles(self):
        roles = await self.roles.list(offset=0, limit=100)
        return list(roles), len(roles)

    async def _get_session_by_access_jti(self, access_jti: str) -> Session | None:
        result = await self.session.execute(select(Session).where(Session.token_jti == access_jti))
        return result.scalar_one_or_none()

    async def _revoke_refresh_tokens_for_session(self, session_id: str, *, now) -> None:
        result = await self.session.execute(
            select(RefreshTokenRepository.model).where(
                RefreshTokenRepository.model.session_id == session_id,
                RefreshTokenRepository.model.revoked_at.is_(None),
            )
        )
        for token_record in result.scalars().all():
            token_record.revoked_at = now

    async def _revoke_all_user_sessions(self, user_id: str, *, now) -> None:
        result = await self.session.execute(select(Session).where(Session.user_id == user_id))
        for session_record in result.scalars().all():
            session_record.status = SessionStatus.REVOKED.value
            session_record.revoked_at = now

        refresh_records = await self.refresh_tokens.list_active_by_user_id(user_id, now=now)
        for token_record in refresh_records:
            token_record.revoked_at = now
