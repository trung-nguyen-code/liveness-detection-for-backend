from fastapi import Depends

from ...dependencies import (
    get_builder,
    get_elastic,
    get_mongo,
    score_settings_path,
    # score_settings_path,
)
from app.domain.user import (
    UserRepository,
)
from app.domain.you_profile import YouProfileRepository
from app.domain.user_interactions import UserInteractionsRepository
from app.domain.score_settings import ScoreSettingsRepository

from app.infrastructure.elasticsearch.user import (
    UserQueryServiceElastic,
)
from app.infrastructure.mongo.user import UserRepositoryMongo
from app.infrastructure.mongo.you_profile import YouProfileRepositoryMongo
from app.infrastructure.mongo.user_interactions import UserInteractionsRepositoryMongo
from app.infrastructure.local_file_system.score_settings import (
    ScoreSettingsRepositoryImpl,
)

from app.usecase.user import (
    UserQueryService,
    UserQueryUseCase,
    UserQueryUseCaseImpl,
    UserRankingUseCaseImpl,
)


def user_query_usecase_recommend(
    elastic=Depends(get_elastic),
    query_builder=Depends(get_builder),
    mongo=Depends(get_mongo),
) -> UserQueryUseCase:
    score_settings: ScoreSettingsRepository = ScoreSettingsRepositoryImpl(
        file_path=score_settings_path
    )

    user_query_service_elastic: UserQueryService = UserQueryServiceElastic(
        elastic, query_builder, score_settings
    )  # noqa: E501
    user_repository_mongo: UserRepository = UserRepositoryMongo(mongo)  # noqa: E501
    you_profile_repository_mongo: YouProfileRepository = YouProfileRepositoryMongo(
        mongo
    )  # noqa: E501
    user_interactions_repository_mongo: UserInteractionsRepository = (
        UserInteractionsRepositoryMongo(mongo)
    )

    return UserQueryUseCaseImpl(
        user_query_service=user_query_service_elastic,
        user_repository=user_repository_mongo,
        user_interactions_repository=user_interactions_repository_mongo,
        you_profile_repository=you_profile_repository_mongo,  # noqa: E501
    )


def user_query_usecase_ranking(
    elastic=Depends(get_elastic),
    query_builder=Depends(get_builder),
    mongo=Depends(get_mongo),
) -> UserQueryUseCase:
    score_settings: ScoreSettingsRepository = ScoreSettingsRepositoryImpl(
        file_path=score_settings_path
    )

    user_query_service_elastic: UserQueryService = UserQueryServiceElastic(
        elastic, query_builder, score_settings
    )  # noqa: E501
    user_repository_mongo: UserRepository = UserRepositoryMongo(mongo)  # noqa: E501
    you_profile_repository_mongo: YouProfileRepository = YouProfileRepositoryMongo(
        mongo
    )  # noqa: E501
    user_interactions_repository_mongo: UserInteractionsRepository = (
        UserInteractionsRepositoryMongo(mongo)
    )

    return UserQueryUseCaseImpl(
        user_query_service=user_query_service_elastic,
        user_repository=user_repository_mongo,
        user_interactions_repository=user_interactions_repository_mongo,
        you_profile_repository=you_profile_repository_mongo,  # noqa: E501
    )


def user_ranking_usecase(
    elastic=Depends(get_elastic),
    query_builder=Depends(get_builder),
    mongo=Depends(get_mongo),
) -> UserQueryUseCase:
    score_settings: ScoreSettingsRepository = ScoreSettingsRepositoryImpl(
        file_path=score_settings_path
    )

    user_query_service_elastic: UserQueryService = UserQueryServiceElastic(
        elastic, query_builder, score_settings
    )  # noqa: E501
    user_repository_mongo: UserRepository = UserRepositoryMongo(mongo)  # noqa: E501
    user_interactions_repository_mongo: UserInteractionsRepository = (
        UserInteractionsRepositoryMongo(mongo)
    )

    return UserRankingUseCaseImpl(
        user_query_service=user_query_service_elastic,
        user_repository=user_repository_mongo,
        user_interactions_repository=user_interactions_repository_mongo,
    )
