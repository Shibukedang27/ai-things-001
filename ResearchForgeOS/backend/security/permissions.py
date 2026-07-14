from collections.abc import Iterable

from backend.exceptions import PermissionDeniedError
from backend.models.user import User


def collect_user_permissions(user: User) -> set[str]:
    return {
        permission.name
        for role in user.roles
        for permission in role.permissions
    }


def assert_permissions(user: User, required_permissions: Iterable[str]) -> None:
    required = set(required_permissions)
    granted = collect_user_permissions(user)
    if "admin:manage" in granted:
        return
    missing = sorted(required - granted)
    if missing:
        raise PermissionDeniedError(
            "Your account is missing required permissions.",
            details={"missing_permissions": missing},
        )
