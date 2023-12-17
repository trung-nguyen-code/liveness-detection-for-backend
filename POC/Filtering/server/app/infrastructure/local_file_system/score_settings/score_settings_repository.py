import json
from typing import Optional

from app.domain.score_settings import (
    ScoreSettingsRepository,
    SettingInput,
    Setting,
)  # noqa

# from .user_dto import UserDTO


class ScoreSettingsRepositoryImpl(ScoreSettingsRepository):
    """ScoreSettingsRepositoryImpl implements CRUD operations."""

    def __init__(self, file_path: str):
        self.file_path = file_path

    def save(self, input: SettingInput) -> Optional[SettingInput]:
        """
        Save settings to file
        """
        for setting in input:
            if isinstance(input[setting], Setting):
                input[setting] = input[setting].__dict__

        with open(self.file_path, "w") as f:
            f.write(json.dumps(input))

    def load(self):
        """
        Load settings to dict
        """
        with open(self.file_path, "r") as f:
            data = json.loads(f.read())
            return data
