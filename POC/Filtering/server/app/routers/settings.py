from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.score_settings import ScoreSettingsRepository, SettingInput

from app.infrastructure.local_file_system.score_settings import (
    ScoreSettingsRepositoryImpl,
)
from app.usecase.score_settings import (
    ScoreSettingQueryUseCase,
    ScoreSettingQueryUseCaseImpl,
)
from app.presentation.schema.score_settings import ErrorMessageScoreSettings

from ..dependencies import score_settings_path, logger

router = APIRouter()


def score_setting_query_usecase() -> ScoreSettingQueryUseCase:
    score_settings: ScoreSettingsRepository = ScoreSettingsRepositoryImpl(
        file_path=score_settings_path
    )

    return ScoreSettingQueryUseCaseImpl(score_settings)


@router.get(
    "/settings",
    # response_model=List[UserReadModel],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorMessageScoreSettings,
        },
    },
    tags=["Settings"],
)
def load_setting(
    score_setting_query_usecase: ScoreSettingQueryUseCase = Depends(
        score_setting_query_usecase
    ),
):
    try:
        return score_setting_query_usecase.load_setting()

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@router.post(
    "/settings",
    # response_model=List[UserReadModel],
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorMessageScoreSettings,
        },
    },
    tags=["Settings"],
)
def save_setting(
    input: SettingInput,
    score_setting_query_usecase: ScoreSettingQueryUseCase = Depends(
        score_setting_query_usecase
    ),
):
    try:
        return score_setting_query_usecase.save_setting(input)

    except Exception as e:
        logger.error(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
