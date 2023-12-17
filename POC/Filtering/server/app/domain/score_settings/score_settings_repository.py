from abc import ABC, abstractmethod
from typing import Optional

from .score_settings import SettingInput


class ScoreSettingsRepository(ABC):
    """ScoreSettingsRepository defines a repository interface for Setting entity."""

    @abstractmethod
    def save(self, input: SettingInput) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    def load(self) -> SettingInput:
        raise NotImplementedError
