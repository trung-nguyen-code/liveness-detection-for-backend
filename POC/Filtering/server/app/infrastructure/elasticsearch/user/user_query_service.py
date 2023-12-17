from datetime import datetime
from dateutil.relativedelta import relativedelta
from typing import List, Optional, Union
from elasticsearch_dsl import Q, Search
from elasticsearch_dsl.query import FunctionScore

from app.constants.user import RangeInput, CommonInput, LocationInput
from app.usecase.user import UserQueryService, UserReadModel
from app.utils.dict import safe_itemgetter

from .user_builder import Builder
from ..database import Elastic
from app.domain.score_settings import ScoreSettingsRepository
from app.utils.dict import extract_key_from_value
from app.presentation.schema.user.user_batch_input import UserBatchInput
from app.constants.localisation import LOCALISATION
from app.constants.user import ELASTIC_PROJECTION

# from app.domain.user import User

# from .user_dto import UserDTO


class UserQueryServiceElastic(UserQueryService):
    """UserQueryServiceElastic implements READ operations"""

    def __init__(
        self,
        elastic: Elastic,
        query_builder: Builder,
        score_setting: ScoreSettingsRepository,  # noqa
    ) -> None:
        self.elastic: Elastic = elastic
        self.query_builder: Builder = query_builder
        self.score_setting: ScoreSettingsRepository = score_setting

    async def find_by_ids(
        self, ids: List[int], project: List[str] = ELASTIC_PROJECTION, limit=100
    ) -> List[UserReadModel]:

        users, totals = await self.elastic.search(
            queries=[Q("terms", id_utilisateur=ids)],
            filters=[],
            functions=[],
            project=project,
            limit=limit,
        )
        return users, totals

    async def search_by_you_profile(
        self, queries: List, filters: List, functions: List, project: List
    ) -> Optional[UserReadModel]:
        return await self.elastic.search(queries, filters, functions, project)

    async def search_similar(
        self,
        inputs: List[UserBatchInput],
        paging: int = 100,
        projection: List = ELASTIC_PROJECTION,
    ) -> Optional[UserReadModel]:  # noqa
        search_list = []
        total_list = []
        for input_dict in inputs:
            (queries, filters, functions) = safe_itemgetter(
                "queries", "filters", "functions"
            )(input_dict)

            s = Search(using=self.elastic.client, index=self.elastic.index)
            s = s.source(projection)

            s = s.extra(track_total_hits=True)
            s = s.query(
                FunctionScore(
                    score_mode="sum",
                    boost_mode="max",
                    functions=functions,
                    query={"bool": {"must": queries, "filter": filters}},
                )
            )
            s = s[0:paging]
            search_list.append(s)
            total_list.append(s.count())
        return await self.elastic.bulk_search(search_list), total_list

    def build_query(
        self, inputs: Union[RangeInput, CommonInput, LocationInput]
    ):  # noqa
        queries = []
        filters = []
        functions = []
        (
            id_genre,
            origins,
            id_localisation,
            pays_code,
            dept_code,
            region_code,
            geoname_id,
            is_new_user,
        ) = safe_itemgetter(
            "id_genre",
            "origins",
            "id_localisation",
            "pays_code",
            "dept_code",
            "region_code",
            "geoname_id",
            "is_new_user",
        )(
            inputs
        )

        settings = self.score_setting.load()
        queries.append(Q("term", id_genre=id_genre))
        queries.append(Q("term", actif=1))
        queries.append(Q("term", ghost=0))
        filters.append(Q("range", taux_remplissage={"gte": 0, "lte": 100}))
        filters.append(Q("range", age={"gte": 18, "lte": 80}))
        filters.append(Q("range", size={"gte": 100, "lte": 200}))

        date_now = datetime.now()
        last_one_year = date_now - relativedelta(years=1)
        filters.append(
            Q(
                "range",
                last_live_time={
                    "gte": last_one_year.isoformat(),
                    "lte": date_now.isoformat(),
                },
            )
        )
        if is_new_user:
            date_now = datetime.now()
            yesterday = date_now - relativedelta(day=1)

            filters.append(
                Q(
                    "range",
                    date_create={
                        "gte": yesterday.isoformat(),
                        "lte": date_now.isoformat(),
                    },
                )
            )
        functions = self.query_builder.parse_range_query(
            functions, inputs, settings
        )  # noqa

        functions, queries = self.query_builder.parse_common_query(
            queries, functions, inputs, settings
        )  # noqa

        functions, queries = self.query_builder.build_origin(
            origins,
            settings.get("origin")["setting_type"],
            functions,
            queries,
            settings.get("origin")["score"],
        )

        functions = self.query_builder.parse_extra_query(
            functions, inputs, settings
        )  # noqa

        if (
            id_localisation
            and isinstance(id_localisation, list)
            and 0 not in id_localisation
        ):
            for id in id_localisation:
                key = extract_key_from_value(LOCALISATION, int(id))
                if key == "SAME_COUNTRY":
                    functions, queries = self.query_builder.build_localisation(
                        pays_code,
                        "pays_code",
                        settings.get("localisation")["setting_type"],
                        functions,
                        queries,
                        settings.get("localisation")["score"],
                    )
                if key == "SAME_DEPARTMENT":
                    functions, queries = self.query_builder.build_localisation(
                        dept_code,
                        "dept_code",
                        settings.get("localisation")["setting_type"],
                        functions,
                        queries,
                        settings.get("localisation")["score"],
                    )
                if key == "SAME_REGION":
                    functions, queries = self.query_builder.build_localisation(
                        region_code,
                        "region_code",
                        settings.get("localisation")["setting_type"],
                        functions,
                        queries,
                        settings.get("localisation")["score"],
                    )
                if key == "SAME_CITY":
                    functions, queries = self.query_builder.build_localisation(
                        geoname_id,
                        "geoname_id",
                        settings.get("localisation")["setting_type"],
                        functions,
                        queries,
                        settings.get("localisation")["score"],
                    )

        return queries, filters, functions

    def build_similar(
        self, inputs: Union[RangeInput, CommonInput, LocationInput]
    ):  # noqa
        queries = []
        filters = []
        functions = []
        (
            id_genre,
            origin,
            latitude,
            longitude,
            min_tall,
            max_tall,
            min_age,
            max_age,
        ) = safe_itemgetter(
            "id_genre",
            "origin",
            "latitude",
            "longitude",
            "min_tall",
            "max_tall",
            "min_age",
            "max_age",
        )(
            inputs
        )
        settings = self.score_setting.load()
        queries.append(Q("term", id_genre=id_genre))
        filters.append(Q("range", taux_remplissage={"gte": 0, "lte": 100}))
        filters.append(Q("range", age={"gte": min_age - 15, "lte": max_age + 15}))
        filters.append(Q("range", interacted_users_number={"gte": 10, "lte": 9999}))

        if min_tall > 100 and max_tall < 200:
            filters.append(
                Q("range", size={"gte": min_tall - 40, "lte": max_tall + 40})
            )

        functions = self.query_builder.parse_range_query(
            functions, inputs, settings
        )  # noqa

        functions, queries = self.query_builder.parse_common_query(
            queries, functions, inputs, settings
        )  # noqa
        functions = self.query_builder.build_distance_query(
            functions, latitude, longitude, settings["distance_score"]
        )  # noqa

        functions, queries = self.query_builder.build_origin(
            origin,
            settings.get("origin")["setting_type"],
            functions,
            queries,
            settings.get("origin")["score"],
        )
        return queries, filters, functions

    def build_ranking(
        self,
        inputs: Union[RangeInput, CommonInput, LocationInput],
        include_ids: List[int] = [],
        is_new_user: bool = False,
    ):  # noqa
        queries = []
        filters = []
        functions = []
        (min_tall, max_tall, min_age, max_age,) = safe_itemgetter(
            "min_tall",
            "max_tall",
            "min_age",
            "max_age",
        )(inputs)

        if is_new_user:
            date_now = datetime.now()
            yesterday = date_now - relativedelta(day=1)

            filters.append(
                Q(
                    "range",
                    date_create={
                        "gte": yesterday.isoformat(),
                        "lte": date_now.isoformat(),
                    },
                )
            )

        settings = self.score_setting.load()
        queries.append(Q("term", actif=1))
        queries.append(Q("term", ghost=0))
        filters.append(Q("range", taux_remplissage={"gte": 0, "lte": 100}))

        date_now = datetime.now()
        last_one_year = date_now - relativedelta(years=1)
        filters.append(
            Q(
                "range",
                last_live_time={
                    "gte": last_one_year.isoformat(),
                    "lte": date_now.isoformat(),
                },
            )
        )

        filters.append(Q("range", age={"gte": min_age - 15, "lte": max_age + 15}))
        if isinstance(include_ids, list) and len(include_ids) > 0:
            queries.append(Q("terms", id_utilisateur=include_ids))

        if (min_tall is not None and max_tall is not None) and (
            min_tall > 140 and max_tall < 200
        ):
            filters.append(
                Q("range", size={"gte": min_tall - 40, "lte": max_tall + 40})
            )

        functions = self.query_builder.parse_range_query(
            functions, inputs, settings
        )  # noqa

        functions = self.query_builder.parse_extra_query(
            functions, inputs, settings
        )  # noqa

        return queries, filters, functions
