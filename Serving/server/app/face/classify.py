"""Face detection using Pytorch MTCNN."""

from enum import Enum
from facenet_pytorch import MTCNN
import torch
# from PIL import Image

class FaceClass(Enum):
    """Classification of face detection"""

    NORMAL = 0
    NOFACE = 1
    MULTI_FACE = 2


class FaceDetector:
    def __init__(self) -> None:
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = MTCNN(
            image_size=224,
            # margin=20,
            post_process=False,
            device=device,
            keep_all=False,
            selection_method="largest",
            thresholds=[0.7, 0.7, 0.7],
            min_face_size=30,
        )
        self.multi_face_model = MTCNN(
            image_size=224,
            post_process=False,
            device=device,
            keep_all=False,
            selection_method="largest",
            thresholds=[0.95, 0.95, 0.95],
            min_face_size=120,
        )

    def detect_multi(self, img):
        """Detect if there is multi face."""
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        print("Running on device: {}".format(device))

        boxes, probability = self.multi_face_model.detect(img)
        if boxes is None:
            return 0, 0
        # multi faces found

        prob = []
        box = boxes[0]
        prob.append(probability[0])
        count = 1
        if len(probability) > 1:
            largest_size = (box[2] - box[0]) * (box[3] - box[1])
            for i in range(1, len(probability)):
                box = boxes[i]
                size = (box[2] - box[0]) * (box[3] - box[1])
                # image size not too small compare to the largest one
                if size > largest_size * 0.6:
                    count += 1
                    prob.append(probability[i])
            # print(probability)
        avg_prob = sum(prob) / len(prob)
        return count, avg_prob
    

    def detect(self, img):
        face_detected, probability = self.model(img, return_prob=True, save_path="test.jpg")

        batch_boxes, batch_probs, batch_points = self.model.detect(img, landmarks=True)
        batch_boxes, batch_probs, batch_points = self.model.select_boxes(
                batch_boxes, batch_probs, batch_points, img, method=self.model.selection_method, 
        )
        face_detected = self.model.extract(img, batch_boxes, save_path="test.jpg")
        # img.crop(batch_boxes[0]).save("test.jpg")
        # Detected face
        if face_detected is not None:
            return face_detected, probability
        else:
            # Rotate to continue detect faces if not found
            for i in range(3):
                angle = (i + 1) * 90
                rotated = img.rotate(angle)
                faces_detected, probability = self.model(rotated, return_prob=True, save_path="test.jpg")
                if faces_detected is not None:
                    return faces_detected, probability

        # Not found any face, return 0 probability
        return None, 0

    def detect_with_box(self, img):
        # Detect faces
        batch_boxes, batch_probs, batch_points = self.model.detect(img, landmarks=True)
        # img.crop(batch_boxes[0]).save("test.jpg")

        # Select faces
        if not self.model.keep_all:
            batch_boxes, batch_probs, batch_points = self.model.select_boxes(
                batch_boxes, batch_probs, batch_points, img, method=self.model.selection_method
            )
        if batch_boxes is not None:
        # Extract faces
            faces = self.model.extract(img, batch_boxes, save_path="test.jpg")

            if faces is not None:
                return faces, batch_boxes, batch_probs
            else:
                for i in range(3):
                    angle = (i + 1) * 90
                    rotated = img.rotate(angle)
                    batch_boxes, batch_probs, batch_points = self.model.detect(rotated, landmarks=True)
                    # Select faces
                    if not self.model.keep_all:
                        batch_boxes, batch_probs, batch_points = self.model.select_boxes(
                            batch_boxes, batch_probs, batch_points, img, method=self.model.selection_method
                        )
                    # Extract faces
                    faces = self.model.extract(rotated, batch_boxes, save_path="test.jpg")
                    if faces is not None:
                        return faces, batch_boxes, batch_probs
        else:
            return None, None, None

