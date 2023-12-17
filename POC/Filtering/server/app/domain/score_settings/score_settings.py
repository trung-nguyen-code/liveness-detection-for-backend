from pydantic import BaseModel


class Setting(BaseModel):
    setting_type: bool
    score: int


class SettingInput(BaseModel):
    religious: Setting
    want_children: Setting
    has_children: Setting
    family_situation: Setting
    degree: Setting
    fume: Setting
    body: Setting
    origin: Setting
    localisation: Setting
    age_score: int
    age_you_score: int
    size_score: int
    push_forward_score: int
    distance_score: int
    last_connection_score: int
    seniority_score: int
    photos_score: int
    profile_filling_score: int
    paging: int
