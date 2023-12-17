class UserInteractions:
    """User interactions represents your collection of UserInteractions as an entity."""

    def __init__(
        self,
        user_id: int,
        ID_TOS,
    ):
        self.user_id: int = user_id
        self.ID_TOS = ID_TOS

    def __eq__(self, o: object) -> bool:
        if isinstance(o, UserInteractions):
            return self.user_id == o.user_id

        return False
