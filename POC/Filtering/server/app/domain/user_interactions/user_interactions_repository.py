from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.user_interactions import UserInteractions


class UserInteractionsRepository(ABC):
    """UserInteractionsRepository defines a repository interface for
    UserInteractions entity."""

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[UserInteractions]:
        raise NotImplementedError

    @abstractmethod
    def find_by_ids(self, ids: List[int]) -> List[UserInteractions]:
        raise NotImplementedError
