from fastapi import Depends

from ...dependencies import (
    get_elastic,
    get_mongo,
    score_settings_path,
    # score_settings_path,
)
from app.infrastructure.elasticsearch.you_profile import (
    YouBuilder, 
    YouProfileQueryServiceElastic
)
from app.domain.user import (
    UserRepository,
)

from app.domain.score_settings import ScoreSettingsRepository


from app.infrastructure.mongo.user import UserRepositoryMongo
from app.infrastructure.local_file_system.score_settings import (
    ScoreSettingsRepositoryImpl,
)

from app.usecase.you_profile import (
    YouProfileQueryUseCaseImpl, YouProfileQueryService, YouProfileQueryUseCase
)


def get_builder():
    query_builder = YouBuilder()
    return query_builder


def you_profile_query_usecase_recommend(
    elastic=Depends(get_elastic),
    query_builder=Depends(get_builder),
    mongo=Depends(get_mongo),
) -> YouProfileQueryUseCase:
    score_settings: ScoreSettingsRepository = ScoreSettingsRepositoryImpl(
        file_path=score_settings_path
    )

    you_profile_query_service_elastic: YouProfileQueryService = YouProfileQueryServiceElastic(  # noqa: E501
        elastic, query_builder, score_settings
    )  # noqa: E501
    user_repository_mongo: UserRepository = UserRepositoryMongo(mongo)  # noqa: E501

    return YouProfileQueryUseCaseImpl(
        you_profile_query_service=you_profile_query_service_elastic,
        user_repository=user_repository_mongo,
    )
