from abc import ABC, abstractmethod
from typing import Optional, List

from .user_query_model import UserReadModel
from app.presentation.schema.user.user_batch_input import UserBatchInput


class UserQueryService(ABC):
    """UserQueryService defines a query service inteface related Book entity."""

    @abstractmethod
    def search_by_you_profile(
        self, queries: List, filters: List, functions: List, project: List
    ) -> Optional[UserReadModel]:
        raise NotImplementedError

    @abstractmethod
    def find_by_ids(self, ids: List[int]) -> List[UserReadModel]:
        raise NotImplementedError

    @abstractmethod
    def search_similar(
        self, inputs: List[UserBatchInput], paging: int, projection: List
    ) -> Optional[UserReadModel]:  # noqa
        raise NotImplementedError
