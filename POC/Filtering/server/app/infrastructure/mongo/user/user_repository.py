from typing import List
from datetime import datetime

from app.domain.user import UserRepository
from app.infrastructure.mongo.database import Mongo
from app.constants.user import PROJECTION


class UserRepositoryMongo(UserRepository):
    """UserRepositoryMongo implements CRUD operations"""

    def __init__(self, mongo: Mongo) -> None:
        self.mongo: Mongo = mongo

    async def find_by_id(self, id: int):
        user_collection = self.mongo.user_collection
        users = await self.mongo.query(
            user_collection, {"id_utilisateur": id}, PROJECTION
        )  # noqa
        return users

    async def find_by_ids(self, ids: List[int], project=PROJECTION) -> List:
        user_collection = self.mongo.user_collection
        users = await self.mongo.query(
            user_collection, {"id_utilisateur": {"$in": ids}}, project
        )
        return users

    async def find_by_date(self, date_start: datetime, date_end: datetime) -> List:
        user_collection = self.mongo.user_collection
        users = await self.mongo.query(
            user_collection,
            {"date_create": {"$gte": date_start, "$lte": date_end}},
            {"id_utilisateur": 1, "_id": 0, "date_create": 1},
        )
        return users
