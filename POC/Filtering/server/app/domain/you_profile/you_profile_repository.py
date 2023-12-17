from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.you_profile import YouProfile


class YouProfileRepository(ABC):
    """YouProfileRepository defines a repository interface for User entity."""

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[YouProfile]:
        raise NotImplementedError

    @abstractmethod
    def find_by_ids(self, ids: List[int]) -> List[YouProfile]:
        raise NotImplementedError
