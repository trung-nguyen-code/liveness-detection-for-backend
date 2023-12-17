import time
from abc import ABC, abstractmethod
from typing import Optional, List

from app.domain.user import UserRepository
from app.domain.user_interactions import UserInteractionsRepository

from .user_query_service import UserQueryService
from .user_query_model import UserReadModel
from app.utils.number import safe_to_int
from app.utils.rad_2_deg import rad_2_deg


class UserRankingUseCase(ABC):
    """UserRankingUseCase defines a ranking usecase inteface related User entity."""

    @abstractmethod
    def pure_rank(self, users_similar: List) -> Optional[UserReadModel]:
        raise NotImplementedError

    @abstractmethod
    def rank(self, users: List) -> Optional[UserReadModel]:
        raise NotImplementedError


class UserRankingUseCaseImpl(UserRankingUseCase):
    def __init__(
        self,
        user_query_service: UserQueryService,
        user_interactions_repository: UserInteractionsRepository,
        user_repository: UserRepository,  # noqa
    ):
        self.user_query_service: UserQueryService = user_query_service
        self.user_repository: UserRepository = user_repository
        self.user_interactions_repository: UserInteractionsRepository = (
            user_interactions_repository
        )

    async def rank(self, users: List) -> Optional[UserReadModel]:
        """rank returns a ranking of users."""
        start_rank = time.time()
        query_list = []
        for user in users:
            age = user["age"]

            min_age = int(age) - 5 if user["id_genre"] == 1 else int(age) - 2
            max_age = int(age) + 2 if user["id_genre"] == 1 else int(age) + 5
            min_tall = safe_to_int(user["size"], 170)
            max_tall = safe_to_int(user["size"], 170)

            queries, filters, functions = self.user_query_service.build_ranking(
                {
                    **user,
                    "min_tall": min_tall,
                    "max_tall": max_tall,
                    "min_age": min_age,
                    "max_age": max_age,
                    "latitude": rad_2_deg(user["latitude"]),
                    "longitude": rad_2_deg(user["longitude"]),
                },
                include_ids=[],
                is_new_user=True,
            )  # noqa
            query_list.append(
                {
                    "queries": queries,
                    "filters": filters,
                    "functions": functions,
                }  # noqa
            )

        responses, total_count = await self.user_query_service.search_similar(
            query_list, paging=200, projection=["id_utilisateur"]
        )  # noqa

        results = []
        for index, response in enumerate(responses):
            result = [
                {
                    "candidate_id": hit.id_utilisateur,
                    "score": hit.meta.score,
                }
                for hit in response
            ]

            results.append(
                {
                    "response": result,
                    "total": total_count[index],
                }
            )
        end_rank = time.time()
        print("Rank time: ", end_rank - start_rank)

        return results

    async def pure_rank(self, users_similar: List) -> Optional[UserReadModel]:
        """pure_rank returns a ranking of users."""

        start_rank = time.time()
        query_list = []
        for user in users_similar:
            candidate_ids = []
            similar_ids = list(
                map(lambda x: int(x["id_utilisateur"]), user["response"])
            )
            start_interactions = time.time()
            users_intertions = await self.user_interactions_repository.find_by_ids(
                similar_ids
            )
            end_interactions = time.time()
            print("Interactions time: ", end_interactions - start_interactions)
            age = user["search_options"]["age"]

            min_age = (
                int(age) - 5
                if user["search_options"]["id_genre"] == 1
                else int(age) - 2
            )
            max_age = (
                int(age) + 2
                if user["search_options"]["id_genre"] == 1
                else int(age) + 5
            )
            min_tall = safe_to_int(user["search_options"]["size"], 170)
            max_tall = safe_to_int(user["search_options"]["size"], 170)
            for current_interaction in users_intertions:
                for user_id in current_interaction["ID_TOS"]:
                    if current_interaction["ID_TOS"][user_id] > 10:
                        candidate_ids.append(int(user_id))

            queries, filters, functions = self.user_query_service.build_ranking(
                {
                    **user,
                    "min_tall": min_tall,
                    "max_tall": max_tall,
                    "min_age": min_age,
                    "max_age": max_age,
                    "latitude": user["search_options"]["latitude"],
                    "longitude": user["search_options"]["longitude"],
                },
                candidate_ids,
            )  # noqa
            query_list.append(
                {
                    "queries": queries,
                    "filters": filters,
                    "functions": functions,
                }  # noqa
            )

        responses, total_count = await self.user_query_service.search_similar(
            query_list, paging=200, projection=["id_utilisateur"]
        )  # noqa

        results = []
        for index, response in enumerate(responses):
            result = [
                {
                    "candidate_id": hit.id_utilisateur,
                    "score": hit.meta.score,
                }
                for hit in response
            ]

            results.append(
                {
                    "response": result,
                    "total": total_count[index],
                }
            )
        end_rank = time.time()
        print("Rank time: ", end_rank - start_rank)

        return results
