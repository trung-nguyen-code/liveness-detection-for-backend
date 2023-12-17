from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.user.user import User
from app.constants.user import PROJECTION


class UserRepository(ABC):
    """UserRepository defines a repository interface for User entity."""

    @abstractmethod
    def find_by_id(self, id: int) -> Optional[User]:
        raise NotImplementedError

    @abstractmethod
    def find_by_ids(self, ids: List[int], project=PROJECTION) -> List[User]:
        raise NotImplementedError

    @abstractmethod
    def find_by_date(self, date_start: datetime, date_end: datetime) -> List[User]:
        raise NotImplementedError
