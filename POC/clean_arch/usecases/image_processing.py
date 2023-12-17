import cv2
import numpy as np
import os
import time

from src.generate_patches import CropImage
from src.utility import parse_model_name
from usecases.usecases_repository.repo_face_detection import RepoFaceDetection



class UsecaseImageProcessing(RepoFaceDetection):
    def __init__(self,MODEL_DIR,model):
        self.MODEL_DIR = MODEL_DIR
        self.model = model
        

    def check_image(self,image: np.ndarray) -> bool:
        height, width, channel = image.shape
        if width / height != 3 / 4:
            print("Image is not appropriate!!!\nHeight/Width should be 4/3.")
            return False
        else:
            return True
    
    def face_detect(self,arr: np.ndarray) :
        # Define cropper and model
        image_cropper = CropImage()
        # MODEL_DIR = "./resources/anti_spoof_models"
        
        # Processing image
        img = cv2.imdecode(arr, -1)  # 'Load it as it is'
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        dim = (480, 640)

        # resize image
        image = cv2.resize(img, dim, interpolation=cv2.INTER_CUBIC)
        # image_name = "test.jpg"

        result = self.check_image(image)
        if result is False:
            return
        image_bbox = self.model.get_bbox(image)
        prediction = np.zeros((1, 3))
        test_speed = 0


        for model_name in os.listdir(self.MODEL_DIR):
            h_input, w_input, model_type, scale = parse_model_name(model_name)
            param = {
                "org_img": image,
                "bbox": image_bbox,
                "scale": scale,
                "out_w": w_input,
                "out_h": h_input,
                "crop": True,
            }
            if scale is None:
                param["crop"] = False
            img = image_cropper.crop(**param)
            start = time.time()
            prediction += self.model.predict(img, os.path.join(self.MODEL_DIR, model_name))
            test_speed += time.time() - start

        label = np.argmax(prediction)
        value = prediction[0][label] / 2
        height, width = image.shape[:2]
        return dict(label=label, value=value, height=height, width=width, test_speed=test_speed, image_bbox=image_bbox)


