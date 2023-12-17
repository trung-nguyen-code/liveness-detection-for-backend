# from typing import List
# from fastapi import HTTPException, status
# from app.infrastructure.mongo.database import Mongo

from app.usecase.user import UserQueryService

# from app.domain.user import User
# from app.constants.user import PROJECTION

# from .user_dto import UserDTO


class UserQueryServiceMongo(UserQueryService):
    """UserQueryServiceMongo implements READ operations"""
