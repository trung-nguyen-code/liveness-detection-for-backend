import time
from abc import ABC, abstractmethod
from typing import List
from functional import seq

from .you_profile_query_service import YouProfileQueryService
from app.domain.user import UserRepository, UsersNotFoundError

# from app.constants.user import ELASTIC_PROJECTION
from app.utils.age import calculateAge
# from app.utils.distance import calculate_distance
# from app.utils.number import safe_to_int
# from app.utils.rad_2_deg import rad_2_deg


class YouProfileQueryUseCase(ABC):
    """YouProfileQueryUseCase defines a query usecase inteface related You Profile entity.""" # noqa

    @abstractmethod
    def search_by_profile(self, ids: List[int]):
        raise NotImplementedError


class YouProfileQueryUseCaseImpl(YouProfileQueryUseCase):
    """YouProfileQueryUseCaseImpl implements a query usecases related You Profile entity.""" # noqa

    def __init__(
        self,
        you_profile_query_service: YouProfileQueryService,
        user_repository: UserRepository,  # noqa
    ):
        self.you_profile_query_service: YouProfileQueryService = you_profile_query_service # noqa
        self.user_repository: UserRepository = user_repository

    def transform_user(self, user):
        return {
            **user,
            "age": calculateAge(user["date_naissance"]),
        }

    async def search_by_profile(self, ids: List[int]):
        start_user_time = time.time()
        users = await self.user_repository.find_by_ids(ids)
        end_user_time = time.time()
        print("User time: ", end_user_time - start_user_time, "s")
        if len(users) == 0:
            raise UsersNotFoundError
        transformed_users = seq(users).map(self.transform_user).to_list() # noqa

        start_time = time.time()
        responses = await self.you_profile_query_service.search_by_profile(transformed_users) # noqa
        end_time = time.time()
        print("Elastic time: ", end_time - start_time, "s")

        return responses

