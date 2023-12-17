from pydantic import BaseModel


class DetectLivnessDTO(BaseModel):
    label: str
    probability: float
    test_speed: float
    bbox: list
    width: int
    height: int
