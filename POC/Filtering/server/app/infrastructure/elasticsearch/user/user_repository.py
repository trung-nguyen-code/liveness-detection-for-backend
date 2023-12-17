from typing import Optional

from app.domain.user import User, UserRepository

# from .user_dto import UserDTO


class UserRepositoryImpl(UserRepository):
    """UserRepositoryImpl implements CRUD operations."""

    def __init__(self, session):
        self.session = session

    def find_by_id(self, id: int) -> Optional[User]:
        return ""
