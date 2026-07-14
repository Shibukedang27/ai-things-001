from collections.abc import Sequence

from sqlalchemy.orm import Session

from backend.exceptions import NotFoundError
from backend.models.user import User
from backend.repositories.user_repository import UserRepository
from backend.schemas.user import UserUpdate


class UserService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)

    def get_user(self, user_id: str) -> User:
        user = self.users.get_with_roles(user_id)
        if user is None:
            raise NotFoundError("User was not found.")
        return user

    def list_users(self, *, offset: int, limit: int) -> Sequence[User]:
        return self.users.list_with_roles(offset=offset, limit=limit)

    def update_user(self, user_id: str, payload: UserUpdate) -> User:
        user = self.get_user(user_id)
        update_data = payload.model_dump(exclude_unset=True)
        if "full_name" in update_data:
            user.full_name = update_data["full_name"]
        self.session.commit()
        return self.get_user(user.id)
