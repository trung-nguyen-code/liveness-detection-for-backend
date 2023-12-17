from typing import Union, List, Tuple
from elasticsearch_dsl import Q

from app.constants.user import CommonInput, LocationInput, FeatureInput
from app.usecase.you_profile.you_profile_query_service import YouProfileQueryService
from app.infrastructure.elasticsearch.database import Elastic
from app.infrastructure.elasticsearch.you_profile.you_profile_builder import YouBuilder
from app.domain.score_settings.score_settings_repository import ScoreSettingsRepository
from app.utils.dict import safe_itemgetter


class YouProfileQueryServiceElastic(YouProfileQueryService):
    """YouProfileQueryServiceElastic implements service"""

    def __init__(
        self,
        elastic: Elastic,
        query_builder: YouBuilder,
        score_setting: ScoreSettingsRepository,  # noqa
    ) -> None:
        self.elastic: Elastic = elastic
        self.query_builder: YouBuilder = query_builder
        self.score_setting: ScoreSettingsRepository = score_setting

    def build_profile_query(
        self, inputs: Union[CommonInput, LocationInput, FeatureInput]
    ) -> Tuple[List, List, List]:  # noqa
        settings = self.score_setting.load()

        queries, filters, functions = [], [], []

        (age, size, id_genre) = safe_itemgetter("age", "size", "id_genre")(inputs)
        # if int(id_genre) == 1:
        #     queries.append(Q("term", id_genre=2))
        # else:
        #     queries.append(Q("term", id_genre=1))

        filters.append(Q("range", age_begin={"gte": 18, "lte": 80}))
        filters.append(Q("range", age_end={"gte": 18, "lte": 80}))
        filters.append(Q("range", taille_begin={"gte": 100, "lte": 200}))
        filters.append(Q("range", taille_end={"gte": 100, "lte": 200}))

        functions = self.query_builder.build_range_query(
            functions, age, "age_begin", "age_end", settings["age_score"]
        )  # noqa
        functions = self.query_builder.build_range_query(
            functions, int(size), "taille_begin", "taille_end", settings["size_score"]
        )  # noqa
        functions, queries = self.query_builder.parse_common_query(
            queries, functions, inputs, settings
        )  # noqa
        # print("functions", functions)

        return queries, filters, functions

    async def search_by_profile(
        self, inputs: List[Union[CommonInput, LocationInput, FeatureInput]]
    ):  # noqa
        query_list = []
        for profile in inputs:
            queries, filters, functions = self.build_profile_query(profile)
            query_list.append(
                {
                    "queries": queries,
                    "filters": filters,
                    "functions": functions,
                    "project": [
                        "id_utilisateur",
                        "age_begin",
                        "age_end",
                        "taille_begin",
                        "taille_end",
                        "pratiquant",
                        "salat_pratique",
                        "v_enfant",
                        "a_enfant",
                        "fumes",
                        "id_nvetudes",
                        "id_physique",
                        "id_statutmarital",
                        "veil",
                    ],
                    "limit": 100,
                }
            )
        results = []
        responses, totals = await self.elastic.multi_search(
            query_list, index="you_profile_utilisateur_221222"
        )  # noqa
        for index, response in enumerate(responses):
            results.append(
                {
                    # "search_options": {
                    #     **users[index],
                    #     "age": calculateAge(users[index]["date_naissance"]),
                    #     "app_origin": users[index].get("app_origin", 0),
                    #     "latitude": rad_2_deg(user["latitude"]),
                    #     "longitude": rad_2_deg(user["longitude"]),
                    # },
                    "response": [
                        {
                            **hit.to_dict(),
                            "score": hit.meta.score,
                        }
                        for hit in response
                    ],
                    "total": totals[index],
                }
            )
        return results
