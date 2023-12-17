from enum import Enum


class CLASSIFIED(Enum):
    """Classification of photo"""

    NORMAL = 0
    NOFACE = 1
    SUNGLASSES = 2
    MULTI_FACES = 3
    FACE_MASK = 4
    NUDE = 5


class PredictorResponse:
    def __init__(
        self, classes=[CLASSIFIED.NORMAL, CLASSIFIED.SUNGLASSES], predictions=[1, 0]
    ):
        self.classes = classes
        self.predictions = predictions

    def get_response(self):
        if self.predictions[0] > self.predictions[1]:
            return {"predict": self.classes[0], "probability": self.predictions[0]}
        else:
            return {"predict": self.classes[1], "probability": self.predictions[1]}
