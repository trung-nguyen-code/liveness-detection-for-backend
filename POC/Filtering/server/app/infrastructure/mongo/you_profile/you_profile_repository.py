from typing import List

from app.domain.you_profile import YouProfileRepository
from app.infrastructure.mongo.database import Mongo
from app.constants.you_profile import PROJECTION


class YouProfileRepositoryMongo(YouProfileRepository):
    """YouProfileRepositoryMongo implements CRUD operations"""

    def __init__(self, mongo: Mongo) -> None:
        self.mongo: Mongo = mongo

    async def find_by_id(self, id: int):
        you_collection = self.mongo.you_collection
        profiles = await self.mongo.query(
            you_collection, {"id_utilisateur": id}, PROJECTION
        )  # noqa
        return profiles

    async def find_by_ids(self, ids: List[int]) -> List:
        you_collection = self.mongo.you_collection
        profiles = await self.mongo.query(
            you_collection, {"id_utilisateur": {"$in": ids}}, PROJECTION
        )

        return profiles
