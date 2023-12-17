from pydantic import BaseModel, Field

from app.domain.user.user_exception import UserNotFoundError, UsersNotFoundError


class ErrorMessageUserNotFound(BaseModel):
    detail: str = Field(example=UserNotFoundError.message)


class ErrorMessageUsersNotFound(BaseModel):
    detail: str = Field(example=UsersNotFoundError.message)
