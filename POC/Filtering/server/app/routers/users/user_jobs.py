import time
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.utils.age import calculateAge

from ...dependencies import (
    logger,
    # score_settings_path,
)
from app.presentation.schema.user.user_error_message import (
    ErrorMessageUserNotFound,
)


from app.usecase.user import (
    UserQueryUseCase,
    UserRankingUseCase,
)
from .injectors import (
    user_query_usecase_recommend,
    user_query_usecase_ranking,
    user_ranking_usecase,
)


router = APIRouter()


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
    "/job/recommends_new",
    # response_model=List[UserReadModel],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessageUserNotFound,
        },
    },
    tags=["Schedule Job"],
)
async def recommends_new(
    user_ids: List[int],
    user_query_usecase: UserQueryUseCase = Depends(user_query_usecase_recommend),
):
    try:
        users = await user_query_usecase.search_by_profiles(user_ids, is_new_user=True)

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

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


@router.post(
    "/job/recommend_search_new",
    # response_model=List[UserReadModel],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessageUserNotFound,
        },
    },
    tags=["Schedule Job"],
)
async def job_recommend_search_new(
    user_ids: List[int],
    user_query_usecase: UserQueryUseCase = Depends(user_query_usecase_ranking),
    user_ranking_usecase: UserRankingUseCase = Depends(user_ranking_usecase),
):
    try:
        users = await user_query_usecase.user_repository.find_by_ids(user_ids)
        users_with_age = []
        for user in users:
            age = calculateAge(user["date_naissance"])
            users_with_age.append({**user, "age": age})
        start_ranking = time.time()
        users = await user_ranking_usecase.rank(users_with_age)
        end_ranking = time.time()
        print("Ranking time: ", end_ranking - start_ranking)

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    # users = await user_query_usecase.rank_candidate(user_ids)

    return users
