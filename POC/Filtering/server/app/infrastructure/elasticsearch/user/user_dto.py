from datetime import datetime
from typing import Union


from app.domain.user import User
from app.usecase.user import UserReadModel


def unixtimestamp() -> int:
    return int(datetime.now().timestamp() * 1000)


class UserDTO:
    """BookDTO is a data transfer object associated with Book entity."""

    def __init__(self, id_utilisateur: int, created_at: Union[int, None] = None):
        self.id_utilisateur = id_utilisateur
        self.created_at = created_at or unixtimestamp()

    def to_entity(self) -> User:
        return User(
            id_utilisateur=self.id_utilisateur,
            created_at=self.created_at,
        )

    def to_read_model(self) -> UserReadModel:
        return UserReadModel(
            id_utilisateur=self.id_utilisateur,
            created_at=self.created_at,
        )

    # @staticmethod
    # def from_entity(user: User) -> "UserDTO":
    #     now = unixtimestamp()
    #     return UserDTO(
    #         id_utilisateur=user.id_utilisateur,
    #         created_at=now,
    #     )
