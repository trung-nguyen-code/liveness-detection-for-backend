from pydantic import BaseModel, Field

from app.domain.score_settings import BadFormatError


class ErrorMessageScoreSettings(BaseModel):
    detail: str = Field(example=BadFormatError.message)
