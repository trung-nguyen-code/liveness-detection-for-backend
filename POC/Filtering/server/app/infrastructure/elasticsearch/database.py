from elasticsearch_dsl import Search, MultiSearch
from elasticsearch_dsl.query import FunctionScore

# from elasticsearch_dsl.query import FunctionScore
from elasticsearch import Elasticsearch
from app.constants.settings import settings
from app.utils.dict import safe_itemgetter


class Elastic:
    def __init__(self) -> None:
        self.client = Elasticsearch(
            settings.ELASTIC_SEARCH,
            ca_certs="/aimatching/app/infrastructure/elasticsearch/elasticsearch-ca.pem",  # noqa
        )
        self.index = settings.ELASTIC_INDEX

    async def search(
        self, queries, filters, functions, project, limit=10, exclude_ids=[]
    ):
        s = Search(using=self.client, index=self.index)

        s = s.source(project)
        s = s.query(
            FunctionScore(
                score_mode="sum",
                boost_mode="max",
                functions=functions,
                query={"bool": {"must": queries, "filter": filters}},
            )
        )

        s = s.exclude("terms", id_utilisateur=exclude_ids)

        s = s[0:limit]

        response = s.execute()
        return response, s.count()

    async def multi_search(self, search_list, index=settings.ELASTIC_INDEX):
        ms = MultiSearch(using=self.client, index=index)
        totals = []
        for search in search_list:
            (queries, filters, functions, project, limit) = safe_itemgetter(
                "queries", "filters", "functions", "project", "limit"
            )(search)
            s = Search(using=self.client, index=index)
            s = s.source(project)
            s = s.query(
                FunctionScore(
                    score_mode="sum",
                    boost_mode="max",
                    functions=functions,
                    query={"bool": {"must": queries, "filter": filters}},
                )
            )
            s = s[0:limit]
            totals.append(s.count())
            ms = ms.add(s)
        responses = ms.execute()
        return responses, totals

    async def bulk_search(self, search_list):
        ms = MultiSearch(using=self.client, index=settings.ELASTIC_INDEX)

        for search in search_list:
            ms = ms.add(search)

        responses = ms.execute()
        return responses
