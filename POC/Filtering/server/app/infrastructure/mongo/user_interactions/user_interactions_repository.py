from typing import List

from app.domain.user_interactions import UserInteractions
from app.infrastructure.mongo.database import Mongo


class UserInteractionsRepositoryMongo(UserInteractions):
    """UserInteractionsRepositoryMongo implements CRUD operations"""

    def __init__(self, mongo: Mongo) -> None:
        self.mongo: Mongo = mongo

    async def find_by_id(self, id: int):
        interactions_collection = self.mongo.interactions_collection
        user_interactions = await self.mongo.query(
            interactions_collection,
            {"user_id": id},
            {"_id": 0, "user_id": 1, "ID_TOS": 1},
        )  # noqa
        return user_interactions

    async def find_by_ids(self, ids: List[int]) -> List:
        interactions_collection = self.mongo.interactions_collection
        user_interactions = await self.mongo.query(
            interactions_collection,
            {"user_id": {"$in": ids}},
            {"_id": 0, "user_id": 1, "ID_TOS": 1},
        )
        return user_interactions
