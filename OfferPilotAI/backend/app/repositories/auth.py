"""Authentication repositories."""

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuthCredential, PasswordResetToken, RefreshToken, Role, Session, UserRole
from app.repositories.base import SQLAlchemyRepository


class AuthCredentialRepository(SQLAlchemyRepository[AuthCredential]):
    model = AuthCredential

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_user_id(self, user_id: str) -> AuthCredential | None:
        result = await self.session.execute(select(AuthCredential).where(AuthCredential.user_id == user_id))
        return result.scalar_one_or_none()


class RoleRepository(SQLAlchemyRepository[Role]):
    model = Role

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_name(self, name: str) -> Role | None:
        result = await self.session.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def list_by_user_id(self, user_id: str) -> Sequence[Role]:
        result = await self.session.execute(
            select(Role)
            .join(UserRole, UserRole.role_id == Role.id)
            .where(UserRole.user_id == user_id)
            .order_by(Role.name.asc())
        )
        return result.scalars().all()


class UserRoleRepository(SQLAlchemyRepository[UserRole]):
    model = UserRole

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_assignment(self, *, user_id: str, role_id: str) -> UserRole | None:
        result = await self.session.execute(
            select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id)
        )
        return result.scalar_one_or_none()


class RefreshTokenRepository(SQLAlchemyRepository[RefreshToken]):
    model = RefreshToken

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        result = await self.session.execute(select(RefreshToken).where(RefreshToken.jti == jti))
        return result.scalar_one_or_none()

    async def get_by_jti_and_hash(self, *, jti: str, token_hash: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.jti == jti, RefreshToken.token_hash == token_hash)
        )
        return result.scalar_one_or_none()

    async def list_active_by_user_id(self, user_id: str, *, now: datetime) -> Sequence[RefreshToken]:
        result = await self.session.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > now,
            )
        )
        return result.scalars().all()


class PasswordResetTokenRepository(SQLAlchemyRepository[PasswordResetToken]):
    model = PasswordResetToken

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_usable_by_hash(self, *, token_hash: str, now: datetime) -> PasswordResetToken | None:
        result = await self.session.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > now,
            )
        )
        return result.scalar_one_or_none()
