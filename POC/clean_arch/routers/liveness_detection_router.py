from fastapi import FastAPI, File
from fastapi.routing import APIRouter
from handlers.handler_liveness import handler_detect_response
from usecases.image_processing import UsecaseImageProcessing
import numpy as np
from src.anti_spoof_predict import AntiSpoofPredict
# app = FastAPI()
router = APIRouter()

def get_model_dir():
    MODEL_DIR="./resources/anti_spoof_models"
    return MODEL_DIR

def get_model():
    model= AntiSpoofPredict(0)
    return model


@router.post("/liveness_detection")
async def liveness_detection(MODEL_DIR: str = get_model_dir(),model = get_model(),file: bytes = File()):
    
    arr = np.asarray(bytearray(file), dtype=np.uint8)
    usecaseDetect= UsecaseImageProcessing(MODEL_DIR = MODEL_DIR, model = model)
    return handler_detect_response(arr,usecaseDetect)