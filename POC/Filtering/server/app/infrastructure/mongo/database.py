import motor.motor_asyncio
from app.constants.settings import settings


class Mongo:
    def __init__(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URI)
        self.db = self.client[settings.MONGO_DB]
        self.user_collection = self.db[settings.MONGO_USER_COLLECTION]
        self.you_collection = self.db[settings.MONGO_YOU_COLLECTION]
        self.interactions_collection = self.db[settings.MONGO_INTERACTIONS_COLLECTION]

    async def query(self, collection, query, project):
        data = [
            record
            async for record in collection.find(
                query,
                project,
            )
        ]
        return data
