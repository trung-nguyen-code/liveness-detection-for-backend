import logging
import os
import cv2
import time
import numpy as np
from urllib.request import Request, urlopen
from logging import config
import re
import inspect
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI, File
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from constants.settings import settings
from downloader import download_folder
from src.anti_spoof_predict import AntiSpoofPredict
from src.generate_patches import CropImage
from src.utility import parse_model_name


config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

app = FastAPI()
origins = [
    "*"
    # "http://localhost.tiangolo.com",
    # "https://localhost.tiangolo.com",
    # "http://localhost",
    # "http://localhost:8080",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_cors_header(request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Liveness detection API",
        version="1.0",
        description="Liveness detection API with security",
        routes=app.routes,
    )

    # Get all routes where jwt_optional() or jwt_required
    api_router = [route for route in app.routes if isinstance(route, APIRoute)]

    for route in api_router:
        path = getattr(route, "path")
        endpoint = getattr(route, "endpoint")
        methods = [method.lower() for method in getattr(route, "methods")]

        for method in methods:
            # access_token
            if (
                re.search("jwt_required", inspect.getsource(endpoint))
                or re.search("fresh_jwt_required", inspect.getsource(endpoint))
                or re.search("jwt_optional", inspect.getsource(endpoint))
            ):
                openapi_schema["paths"][path][method]["security"] = [
                    {"Bearer Auth": []}
                ]
        for method in methods:
            # refresh_token
            if re.search("jwt_refresh_token_required", inspect.getsource(endpoint)):
                openapi_schema["paths"][path][method]["security"] = [
                    {"Bearer Auth": []}
                ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return _app


app = get_application()
app.openapi = custom_openapi
# setting route

MODEL_DIR = "./resources/anti_spoof_models"

anti_spoof_model = AntiSpoofPredict(0)
image_cropper = CropImage()


# mp_face_detection = mp.solutions.face_detection
# mp_drawing = mp.solutions.drawing_utils


def check_image(image: np.ndarray) -> bool:
    height, width, channel = image.shape
    if width / height != 3 / 4:
        print("Image is not appropriate!!!\nHeight/Width should be 4/3.")
        return False
    else:
        return True


@app.post("/liveness_detection")
async def liveness_detection(file: bytes = File()):
    # req = Request(
    #     url="https://static-staging.mektoube.fr/2/3380/__wMyYDM4MzM/__ANyUzM18554532351bf04bebe466aa8d1dc845451eab97d097411cb99392307d1fb1a374466.jpg",
    #     headers={"User-Agent": "Mozilla/5.0"},
    # )
    # res = urlopen(req)
    # arr = np.asarray(bytearray(res.read()), dtype=np.uint8)
    arr = np.asarray(bytearray(file), dtype=np.uint8)

    img = cv2.imdecode(arr, -1)  # 'Load it as it is'
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    dim = (480, 640)

    # resize image
    image = cv2.resize(img, dim, interpolation=cv2.INTER_CUBIC)
    # image_name = "test.jpg"

    result = check_image(image)
    if result is False:
        return
    image_bbox = anti_spoof_model.get_bbox(image)
    prediction = np.zeros((1, 3))
    test_speed = 0

    for model_name in os.listdir(MODEL_DIR):
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
        prediction += anti_spoof_model.predict(img, os.path.join(MODEL_DIR, model_name))
        test_speed += time.time() - start

    label = np.argmax(prediction)
    print("Label: ",label)
    value = prediction[0][label] / 2
    print("Value: ",value)
    height, width = image.shape[:2]

    resp = {}
    if label == 1 and value >= 0.8:
        print("Prediction cost {:.2f} s".format(test_speed))
        resp = {
            "label": "RealFace" if label == 1 else "FakeFace",
            "probability": value,
            "cost": test_speed,
            "bbox": image_bbox,
            "width": width,
            "height": height,
        }
    else:
        resp = {
            "label": "FakeFace",
            "probability": value,
            "cost": test_speed,
            "bbox": image_bbox,
            "width": width,
            "height": height,
        }
    response = JSONResponse(content=resp)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response
