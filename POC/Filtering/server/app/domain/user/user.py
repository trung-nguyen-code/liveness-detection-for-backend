from typing import Optional


class User:
    """User represents your collection of User as an entity."""

    def __init__(
        self,
        id_utilisateur: int,
        created_at: Optional[int] = None,
    ):
        self.id_utilisateur: int = id_utilisateur
        self.created_at: Optional[int] = created_at

    def __eq__(self, o: object) -> bool:
        if isinstance(o, User):
            return self.id_utilisateur == o.id_utilisateur

        return False
