import cv2
import torch
from PIL import Image
import numpy as np

# Model
model = torch.hub.load("ultralytics/yolov5", "yolov5m")
model.classes = [0]
model.conf = 0.7  # confidence threshold (0-1)
model.iou = 0.7

# Convert the input image to a NumPy array once
def img_to_np(img):
    return np.array(img.convert("RGB"))

def crop_person(img):
    # Convert the image to BGR format

    frame = cv2.cvtColor(img_to_np(img), cv2.COLOR_RGB2BGR)
    # Run the YOLOv5 model
    detections = model(img_to_np(img))
    results = detections.pandas().xyxy[0].to_dict(orient="records")
    person_img = []
    for result in results:
        con = result["confidence"]
        cs = result["class"]
        x1 = int(result["xmin"])
        y1 = int(result["ymin"])
        x2 = int(result["xmax"])
        y2 = int(result["ymax"])
        # Do whatever you want
        image = frame[y1:y2, x1:x2]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        im_pil = Image.fromarray(image)
        # im_pil.show()
        person_img.append(im_pil)
    return person_img
