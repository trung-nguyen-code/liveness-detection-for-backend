from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from ...dependencies import (
    logger,
    # score_settings_path,
)
from app.presentation.schema.user.user_error_message import (
    ErrorMessageUserNotFound,
)


from app.usecase.you_profile import (
    YouProfileQueryUseCase
)
from .injectors import you_profile_query_usecase_recommend


router = APIRouter()


@router.post(
    "/recommend_profiles",
    # response_model=List[UserReadModel],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": ErrorMessageUserNotFound,
        },
    },
    tags=["Recommendations"],
)
async def recommend_profiles(
    user_ids: List[int],
    you_profile_query_usecase: YouProfileQueryUseCase = Depends(you_profile_query_usecase_recommend),  # noqa: E501
):
    users = await you_profile_query_usecase.search_by_profile(user_ids)
    # try:
    #     users = await you_profile_query_usecase.search_by_profile(user_ids)

    # except Exception as e:
    #     logger.error(e)
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #     )

    return users
