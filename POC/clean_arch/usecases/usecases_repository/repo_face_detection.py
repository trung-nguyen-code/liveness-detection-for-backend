from abc import ABC, abstractmethod
import numpy as np

class RepoFaceDetection(ABC):
    @abstractmethod
    def check_image(self,image: np.ndarray) -> bool:
        ...
    @abstractmethod
    def face_detect(self,image: np.ndarray):
        ...