from pydantic import BaseModel
from typing import List


class UserBatchInput(BaseModel):
    user_id: int
    queries: List
    filters: List
    functions: List
