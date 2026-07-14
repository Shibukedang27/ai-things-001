from pydantic import Field

from backend.schemas.common import APIModel, TimestampedRead


class PermissionRead(TimestampedRead):
    id: str
    name: str
    resource: str
    action: str
    description: str


class RoleBase(APIModel):
    name: str = Field(min_length=2, max_length=80, pattern=r"^[a-z][a-z0-9_-]*$")
    description: str = Field(min_length=4, max_length=255)


class RoleCreate(RoleBase):
    permission_names: list[str] = Field(default_factory=list)


class RoleUpdate(APIModel):
    description: str | None = Field(default=None, min_length=4, max_length=255)
    permission_names: list[str] | None = None


class RoleRead(RoleBase, TimestampedRead):
    id: str
    is_system: bool
    permissions: list[PermissionRead] = Field(default_factory=list)
