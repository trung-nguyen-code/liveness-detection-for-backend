import logging
from logging import config
import re
import inspect
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI, Query
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
import torchvision.transforms as T
from PIL import Image
import tensorflow as tf
import time
import asyncio
import numpy as np
import torch
import cv2

from app.face.classify import FaceDetector
from app.utils.image import get_image_from_url, get_image_from_path
from app.constants.settings import settings
from app.libs.predictor import Predictor
from app.person.detect import crop_person
from app.dtos.predictor_response import CLASSIFIED

config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

app = FastAPI()
face_detector = FaceDetector()
sun_glasses_predictor = Predictor(
    base_host=settings.TF_SERVING_HOST,
    path="/v1/models/sunglasses:predict",
    model_name="sunglasses",
    classes=[CLASSIFIED.NORMAL, CLASSIFIED.SUNGLASSES],
)
face_mask_predictor = Predictor(
    base_host=settings.TF_SERVING_HOST,
    path="/v1/models/face_mask:predict",
    model_name="face_mask",
    classes=[CLASSIFIED.FACE_MASK, CLASSIFIED.NORMAL],
)
nude_nonude_predictor = Predictor(
    base_host=settings.TF_SERVING_HOST,
    path="/v1/models/nude_nonude:predict",
    model_name="nude_nonude",
    classes=[CLASSIFIED.NORMAL, CLASSIFIED.NUDE],
)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="AI services API",
        version="1.0",
        description="AI services",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": """
            Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token
            """,
        }
    }

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
# user route

@app.get("/classify")
async def classify(url: str = Query(..., description="URL of image to classify")):
    img = get_image_from_path(url)
    response = {
        "predict": str(CLASSIFIED.NORMAL.value),
        "probability": "1.0",
    }
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

    start_face = time.time()
    detected, boxes, _ = face_detector.detect_with_box(img)
    # print("boxes: ", boxes)
    end_face = time.time()
    if boxes is not None and not isinstance(boxes, list): 
        response["boxes"] = boxes.tolist()
    print("Face detection time: ", end_face - start_face)
    if detected is None:
        response["predict"] = str(CLASSIFIED.NOFACE.value)
        return response
    else:
        # check if multi faces detected
        nb_faces, prob_multi = face_detector.detect_multi(img)
        if (nb_faces) > 1:
            return {
                "predict": str(CLASSIFIED.MULTI_FACES.value),
                "probability": str(prob_multi),
            }

        img_numpy = detected.to(device).numpy()
        # img_numpy = img_numpy.reshape((3, 224, 224))
        img_numpy = np.transpose(img_numpy, (1, 2, 0))
        # sunglasses
        sunglasses_prediction_coroutine = sun_glasses_predictor.predict_rpc(img_numpy)
        # face mask
        face_mask_prediction_coroutine = face_mask_predictor.predict_rpc(img_numpy)
        # Execute the sunglasses and face mask prediction coroutines concurrently
        predictions = await asyncio.gather(sunglasses_prediction_coroutine, face_mask_prediction_coroutine)
        sunglasses_prediction, face_mask_prediction = predictions
        if (
            sunglasses_prediction["predict"] == CLASSIFIED.SUNGLASSES
            and sunglasses_prediction["probability"] > 0.9
        ):
            return {
                "predict": str(CLASSIFIED.SUNGLASSES.value),
                "probability": str(sunglasses_prediction["probability"]),
            }
        elif (
            face_mask_prediction["predict"] == CLASSIFIED.FACE_MASK
            and face_mask_prediction["probability"] > 0.98
        ):
            return {
                "predict": str(CLASSIFIED.FACE_MASK.value),
                "probability": str(face_mask_prediction["probability"]),
            }
        
        start_person = time.time()
        imgs = crop_person(img)
        end_person = time.time()
        print("Person detection time: ", end_person - start_person)
        if len(imgs) > 0:
            for index, person in enumerate(imgs):
                # person.save(f"person{index}.jpg")
                person = person.resize((224, 224), resample=Image.LANCZOS)
                # person.save(f"person{index}.jpg")
                person = np.array(person)
                # nude_nonude_prediction = await nude_nonude_predictor.predict(person)
                nude_nonude_prediction = await nude_nonude_predictor.predict_rpc(person)
                print(nude_nonude_prediction)
                if (
                    nude_nonude_prediction["predict"] == CLASSIFIED.NUDE
                    and nude_nonude_prediction["probability"] > 0.95
                ):
                    return {
                        "predict": str(CLASSIFIED.NUDE.value),
                        "probability": str(nude_nonude_prediction["probability"]),
                    }
    
    return response
