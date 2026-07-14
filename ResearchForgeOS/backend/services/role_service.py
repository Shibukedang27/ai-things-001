from collections.abc import Sequence

from sqlalchemy.orm import Session

from backend.exceptions import ConflictError, NotFoundError, ValidationError
from backend.models.permission import Permission
from backend.models.role import Role
from backend.repositories.permission_repository import PermissionRepository
from backend.repositories.role_repository import RoleRepository
from backend.schemas.role import RoleCreate, RoleUpdate


class RoleService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.roles = RoleRepository(session)
        self.permissions = PermissionRepository(session)

    def list_roles(self, *, offset: int, limit: int) -> Sequence[Role]:
        return self.roles.list_with_permissions(offset=offset, limit=limit)

    def list_permissions(self) -> Sequence[Permission]:
        return self.permissions.list_all()

    def get_role(self, role_id: str) -> Role:
        role = self.roles.get_with_permissions(role_id)
        if role is None:
            raise NotFoundError("Role was not found.")
        return role

    def create_role(self, payload: RoleCreate) -> Role:
        if self.roles.get_by_name(payload.name):
            raise ConflictError("A role with this name already exists.")

        permissions = self._resolve_permissions(payload.permission_names)
        role = Role(
            name=payload.name,
            description=payload.description,
            is_system=False,
            permissions=permissions,
        )
        self.roles.add(role)
        self.session.commit()
        return self.get_role(role.id)

    def update_role(self, role_id: str, payload: RoleUpdate) -> Role:
        role = self.get_role(role_id)
        update_data = payload.model_dump(exclude_unset=True)
        if "description" in update_data:
            role.description = update_data["description"]
        if "permission_names" in update_data and update_data["permission_names"] is not None:
            role.permissions = self._resolve_permissions(update_data["permission_names"])
        self.session.commit()
        return self.get_role(role.id)

    def _resolve_permissions(self, permission_names: Sequence[str]) -> list[Permission]:
        permissions = self.permissions.get_many_by_names(permission_names)
        found_names = {permission.name for permission in permissions}
        missing_names = sorted(set(permission_names) - found_names)
        if missing_names:
            raise ValidationError(
                "One or more permissions do not exist.",
                details={"missing_permissions": missing_names},
            )
        return permissions
