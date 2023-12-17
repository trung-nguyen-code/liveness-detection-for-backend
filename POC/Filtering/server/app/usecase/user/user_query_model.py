# from typing import cast

from pydantic import BaseModel, Field

# from app.domain.user.user import User


class UserReadModel(BaseModel):
    """UserReadModel represents data structure as a read model."""

    def __init__(self, id_utilisateur: int, created_at: int) -> None:
        self.id_utilisateur = id_utilisateur
        self.created_at = created_at

    id_utilisateur: int = Field(example=4)

    created_at: int = Field(example=1136214245000)
