import time
from abc import ABC, abstractmethod
from typing import Optional, List

from .user_query_model import UserReadModel
from .user_query_service import UserQueryService
from app.domain.user import UserRepository, UsersNotFoundError
from app.domain.you_profile import YouProfileRepository, ProfilesNotFoundError
from app.domain.user_interactions import UserInteractionsRepository

from app.constants.user import ELASTIC_PROJECTION
from app.utils.age import calculateAge
from app.utils.distance import calculate_distance
from app.utils.number import safe_to_int
from app.utils.rad_2_deg import rad_2_deg


class UserQueryUseCase(ABC):
    """UserQueryUseCase defines a query usecase inteface related User entity."""

    @abstractmethod
    def search_by_profile(self, id: int) -> Optional[UserReadModel]:
        raise NotImplementedError

    @abstractmethod
    def search_by_profiles(
        self, ids: List[int], is_new_user: bool
    ) -> List[UserReadModel]:
        raise NotImplementedError

    @abstractmethod
    def search_similar(
        self, ids: List[int], paging: int, projection: List[str]
    ) -> Optional[UserReadModel]:
        raise NotImplementedError

    @abstractmethod
    def rank_candidate(self, ids: List[int]) -> Optional[UserReadModel]:
        raise NotImplementedError

    @abstractmethod
    def search_profile(self, id: int) -> Optional[UserReadModel]:
        raise NotImplementedError


class UserQueryUseCaseImpl(UserQueryUseCase):
    """UserQueryUseCaseImpl implements a query usecases related User entity."""

    def __init__(
        self,
        user_query_service: UserQueryService,
        you_profile_repository: YouProfileRepository,
        user_interactions_repository: UserInteractionsRepository,
        user_repository: UserRepository,  # noqa
    ):
        self.user_query_service: UserQueryService = user_query_service
        self.user_repository: UserRepository = user_repository
        self.user_interactions_repository: UserInteractionsRepository = (
            user_interactions_repository
        )
        self.you_profile_repository: YouProfileRepository = (
            you_profile_repository  # noqa
        )

    async def search_similar(
        self,
        ids: List[int],
        paging: int = 100,
        projection: List[str] = ELASTIC_PROJECTION,
    ) -> Optional[UserReadModel]:
        print("ids", ids)
        users, _ = await self.user_query_service.find_by_ids(ids)
        users = list(map(lambda user: user.to_dict(), users))

        query_list = []
        for user in users:
            queries, filters, functions = self.user_query_service.build_similar(
                {
                    **user,
                    "min_tall": safe_to_int(user["size"], 170),
                    "max_tall": safe_to_int(user["size"], 170),
                    "min_age": safe_to_int(user["age"], 18),
                    "max_age": safe_to_int(user["age"], 18),
                    "latitude": rad_2_deg(user["latitude"]),
                    "longitude": rad_2_deg(user["longitude"]),
                }
            )  # noqa
            query_list.append(
                {
                    "queries": queries,
                    "filters": filters,
                    "functions": functions,
                    "user_id": user["id_utilisateur"],
                }  # noqa
            )

        responses, total_count = await self.user_query_service.search_similar(
            query_list, paging, projection=projection
        )  # noqa
        start_time = time.time()

        results = []
        for index, response in enumerate(responses):
            results.append(
                {
                    "search_options": {
                        **users[index],
                        "latitude": rad_2_deg(users[index]["latitude"]),
                        "longitude": rad_2_deg(users[index]["longitude"]),
                    },
                    "response": [
                        {
                            **hit.to_dict(),
                            "score": hit.meta.score,
                        }
                        for hit in response
                    ],
                    "total": total_count[index],
                }
            )
        end_time = time.time()
        print("Time to map: ", end_time - start_time)
        return results

    async def search_by_profiles(
        self, ids: List[int], is_new_user: bool = False
    ) -> List[UserReadModel]:
        users = await self.user_repository.find_by_ids(ids)
        if len(users) == 0:
            raise UsersNotFoundError
        profiles = await self.you_profile_repository.find_by_ids(ids)
        if len(profiles) == 0:
            raise ProfilesNotFoundError

        query_list = []

        for index, user in enumerate(users):
            search_options = {
                **user,
                **profiles[index],
                "min_tall": profiles[index]["taille_begin"],
                "max_tall": profiles[index]["taille_end"],
                "min_age": profiles[index]["age_begin"] - 5
                if user["id_genre"] == 1
                else profiles[index]["age_begin"] - 4,
                "max_age": profiles[index]["age_end"] + 4
                if user["id_genre"] == 1
                else profiles[index]["age_end"] + 5,
                "id_genre": 2 if user["id_genre"] == 1 else 1,
                "want_children": profiles[index]["v_enfant"],
                "has_children": profiles[index]["a_enfant"],
                "family_situation": profiles[index]["id_statutmarital"],
                "study_level": profiles[index]["id_nvetudes"],
                "figure": profiles[index]["id_physique"],
                "fume": profiles[index]["fumes"],
                "latitude": rad_2_deg(user["latitude"]),
                "longitude": rad_2_deg(user["longitude"]),
                "is_new_user": is_new_user,
            }
            queries, filters, functions = self.user_query_service.build_query(
                search_options
            )
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
                    **hit.to_dict(),
                    "score": hit.meta.score,
                }
                for hit in response
            ]
            results.append({"response": result, "total": total_count[index]})
        return results

    async def search_by_profile(self, id: int) -> Optional[UserReadModel]:
        users = await self.user_repository.find_by_ids([id])
        if len(users) == 0:
            raise UsersNotFoundError
        profiles = await self.you_profile_repository.find_by_ids([id])
        if len(profiles) == 0:
            raise ProfilesNotFoundError

        search_options = {
            **users[0],
            **profiles[0],
            "min_tall": profiles[0]["taille_begin"],
            "max_tall": profiles[0]["taille_end"],
            "min_age": profiles[0]["age_begin"] - 5
            if users[0]["id_genre"] == 1
            else profiles[0]["age_begin"] - 4,
            "max_age": profiles[0]["age_end"] + 4
            if users[0]["id_genre"] == 1
            else profiles[0]["age_end"] + 5,
            "id_genre": 2 if users[0]["id_genre"] == 1 else 1,
            "want_children": profiles[0]["v_enfant"],
            "has_children": profiles[0]["a_enfant"],
            "family_situation": profiles[0]["id_statutmarital"],
            "study_level": profiles[0]["id_nvetudes"],
            "figure": profiles[0]["id_physique"],
            "fume": profiles[0]["fumes"],
            "latitude": rad_2_deg(users[0]["latitude"]),
            "longitude": rad_2_deg(users[0]["longitude"]),
        }

        queries, filters, functions = self.user_query_service.build_query(
            search_options
        )
        response, total = await self.user_query_service.search_by_you_profile(
            queries, filters, functions, ELASTIC_PROJECTION
        )

        results = [
            {
                "photos": hit.photos.to_dict() if hit.photos else {},
                "candidate_id": hit.id_utilisateur,
                "id_genre": hit.id_genre,
                "age": hit.age,
                "size": hit.size,
                "religious": hit.is_pratiquant,
                "salat_pratique": hit.salat_pratique,
                "veil": hit.veil,
                "eat_halal": hit.eat_halal,
                "want_children": hit.want_children,
                "has_children": hit.has_children,
                "family_situation": hit.family_situation,
                "degree": hit.study_level,
                "fume": hit.fume,
                "body": hit.figure,
                "pays_code": hit.pays_code,
                "dept_code": hit.dept_code,
                "region_code": hit.region_code,
                "geoname_id": hit.geoname_id,
                "date_mise_avant": hit.date_mise_avant,
                "last_live_time": hit.last_live_time,
                "date_create": hit.date_create,
                "profile_filling_rate": hit.taux_remplissage,
                "origin": list(hit.origin) if hit.origin else [],
                "latitude": hit.location["lat"],
                "longitude": hit.location["lon"],
                "score": hit.meta.score,
            }
            for hit in response
        ]

        distances = await calculate_distance(
            {
                "latitude": rad_2_deg(users[0]["latitude"]),
                "longitude": rad_2_deg(users[0]["longitude"]),
            },
            results,
        )
        candidates_distance = []

        for index, result in enumerate(results):
            candidates_distance.append({**result, "distances": distances[index]})

        return {
            "search_options": {
                **users[0],
                **profiles[0],
                "age": calculateAge(users[0]["date_naissance"]),
                "min_tall": profiles[0]["taille_begin"],
                "max_tall": profiles[0]["taille_end"],
                "min_age": profiles[0]["age_begin"] - 5
                if users[0]["id_genre"] == 1
                else profiles[0]["age_begin"] - 4,
                "max_age": profiles[0]["age_end"] + 4
                if users[0]["id_genre"] == 1
                else profiles[0]["age_end"] + 5,
                "want_children": profiles[0]["v_enfant"],
                "has_children": profiles[0]["a_enfant"],
                "family_situation": profiles[0]["id_statutmarital"],
                "study_level": profiles[0]["id_nvetudes"],
                "figure": profiles[0]["id_physique"],
                "fume": profiles[0]["fumes"],
            },
            "result": candidates_distance,
            "total": total,
        }

    async def rank_candidate(self, ids: List[int]) -> Optional[UserReadModel]:
        start_similar = time.time()
        users_similar = await self.search_similar(
            ids,
            paging=100,
            # projection=["id_utilisateur"]
        )
        end_similar = time.time()
        print("Similar time: ", end_similar - start_similar)

        start_rank = time.time()
        query_list = []

        for user in users_similar:
            candidate_ids = []
            similar_ids = list(
                map(lambda x: int(x["id_utilisateur"]), user["response"])
            )
            users_intertions = await self.user_interactions_repository.find_by_ids(
                similar_ids
            )
            age = calculateAge(user["search_options"]["date_naissance"])

            # min_age = int(age)
            # max_age = int(age)
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
                for user_id in current_interaction["ID_TOS"].keys():
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
            query_list,
            paging=200,
            # projection=["id_utilisateur"]
        )  # noqa
        print("total_count", total_count)
        results = []
        for index, response in enumerate(responses):
            result = [
                {
                    **hit.to_dict(),
                    "latitude": hit.location["lat"],
                    "longitude": hit.location["lon"],
                    "location": None,
                    "candidate_id": hit.id_utilisateur,
                    "score": hit.meta.score,
                    "match_count": total_count[index],
                }
                for hit in response
            ]
            distances = await calculate_distance(
                {
                    "latitude": users_similar[index]["search_options"]["latitude"],
                    "longitude": users_similar[index]["search_options"]["longitude"],
                },
                result,
            )
            result = [
                {
                    **item,
                    "distance": distances[index],
                }
                for index, item in enumerate(result)
            ]

            results.append(
                {
                    "search_options": {
                        **users_similar[index]["search_options"],
                        "age": calculateAge(
                            users_similar[index]["search_options"]["date_naissance"]
                        ),
                        "pratiquant": users_similar[index]["search_options"][
                            "is_pratiquant"
                        ],
                    },
                    "response": result,
                    "total": total_count[index],
                }
            )
        end_rank = time.time()
        print("Rank time: ", end_rank - start_rank)

        return results

    async def search_profile(self, id: int) -> Optional[UserReadModel]:
        user = await self.user_repository.find_by_id(id)
        if not user:
            raise UsersNotFoundError

        return user
