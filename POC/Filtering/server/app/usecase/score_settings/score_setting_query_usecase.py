from abc import ABC, abstractmethod
from typing import Optional

from app.domain.score_settings import SettingInput, ScoreSettingsRepository


class ScoreSettingQueryUseCase(ABC):
    """ScoreSettingQueryUseCase defines a query usecase inteface
    related score setting entity."""

    @abstractmethod
    def load_setting(self) -> Optional[SettingInput]:
        raise NotImplementedError

    @abstractmethod
    def save_setting(self, input: SettingInput) -> Optional[SettingInput]:
        raise NotImplementedError


class ScoreSettingQueryUseCaseImpl(ScoreSettingQueryUseCase):
    """ScoreSettingQueryUseCaseImpl implements a query usecases
    related User entity."""

    def __init__(self, score_settings_repository: ScoreSettingsRepository):
        self.score_settings_repository: ScoreSettingsRepository = (
            score_settings_repository
        )

    def load_setting(self) -> Optional[SettingInput]:
        return self.score_settings_repository.load()

    def save_setting(self, input: SettingInput) -> Optional[SettingInput]:
        return self.score_settings_repository.save(input)
