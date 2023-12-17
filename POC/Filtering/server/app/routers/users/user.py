import time
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from ...dependencies import (
    logger,
    # score_settings_path,
)
from app.domain.user import (
    UserNotFoundError,
)
from app.presentation.schema.user.user_error_message import (
    ErrorMessageUserNotFound,
)


from app.usecase.user import (
    UserQueryUseCase,
    UserRankingUseCase,
)
from .injectors import (
    user_query_usecase_ranking,
    user_query_usecase_recommend,
    user_ranking_usecase,
)


router = APIRouter()


@router.get(
    "/recommend/{user_id}",
    # response_model=List[UserReadModel],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessageUserNotFound,
        },
    },
    tags=["Recommendations"],
)
async def recommend(
    user_id: int,
    user_query_usecase: UserQueryUseCase = Depends(user_query_usecase_recommend),
):
    try:
        user = await user_query_usecase.search_by_profile(user_id)

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=UserNotFoundError.message,
        )

    return user


@router.post(
    "/job/recommends",
    # response_model=List[UserReadModel],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessageUserNotFound,
        },
    },
    tags=["Schedule Job"],
)
async def recommends(
    user_ids: List[int],
    user_query_usecase: UserQueryUseCase = Depends(user_query_usecase_recommend),
):
    try:
        users = await user_query_usecase.search_by_profiles(user_ids)

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return users


@router.post(
    "/similar_search",
    # response_model=List[UserReadModel],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessageUserNotFound,
        },
    },
    tags=["Recommendations"],
)
async def similar_search(
    user_ids: List[int],
    user_query_usecase: UserQueryUseCase = Depends(user_query_usecase_ranking),
):
    try:
        users = await user_query_usecase.search_similar(user_ids)

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return users


@router.post(
    "/recommend_search",
    # response_model=List[UserReadModel],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessageUserNotFound,
        },
    },
    tags=["Ranking"],
)
async def recommend_search(
    user_ids: List[int],
    user_query_usecase: UserQueryUseCase = Depends(user_query_usecase_ranking),
):
    try:
        users = await user_query_usecase.rank_candidate(user_ids)

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    # users = await user_query_usecase.rank_candidate(user_ids)

    return users


@router.post(
    "/job/recommend_search",
    # response_model=List[UserReadModel],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessageUserNotFound,
        },
    },
    tags=["Schedule Job"],
)
async def job_recommend_search(
    user_ids: List[int],
    user_query_usecase: UserQueryUseCase = Depends(user_query_usecase_ranking),
    user_ranking_usecase: UserRankingUseCase = Depends(user_ranking_usecase),
):
    try:
        start_similar = time.time()
        users_similar = await user_query_usecase.search_similar(
            user_ids, paging=100, projection=["id_utilisateur"]
        )
        end_similar = time.time()
        print("Similar time: ", end_similar - start_similar)
        start_ranking = time.time()
        users = await user_ranking_usecase.pure_rank(users_similar)
        end_ranking = time.time()
        print("Ranking time: ", end_ranking - start_ranking)

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    # users = await user_query_usecase.rank_candidate(user_ids)

    return users
