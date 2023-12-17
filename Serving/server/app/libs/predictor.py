import json
from pydantic import BaseModel
from PIL import Image
import numpy as np
import aiohttp

import asyncio
import grpc
import time
from tensorflow_serving.apis import predict_pb2
from tensorflow_serving.apis import prediction_service_pb2_grpc
import tensorflow as tf

from app.dtos.predictor_response import PredictorResponse
from app.dtos.predictor_response import CLASSIFIED
from app.libs.model_mapping import RPC_Mapping
# Set the content type header
headers = {"content-type": "application/json"}


class Response(BaseModel):
    predict: str
    probability: float


class Predictor:
    def __init__(self, 
                 base_host,
                 path, 
                 rest_port=8501,
                 grpc_port=8500,
                 classes=[CLASSIFIED.NORMAL, CLASSIFIED.SUNGLASSES],
                 model_name='sunglasses'
                 ):
        self.host = base_host
        self.path = path
        self.rest_port = rest_port
        self.grpc_port = grpc_port
        self.classes = classes
        self.model_name = model_name

    async def predict_rpc(self, img):
        image_array = img.astype("float32")
        # Create gRPC channel and stub
        channel = grpc.aio.insecure_channel(f'{self.host}:{self.grpc_port}')
        stub = prediction_service_pb2_grpc.PredictionServiceStub(channel)

        # Create prediction request
        request = predict_pb2.PredictRequest()
        request.model_spec.name = self.model_name
        request.model_spec.signature_name = 'serving_default'
        request.inputs[str(RPC_Mapping[self.model_name].value)].CopyFrom(
            tf.make_tensor_proto(image_array, shape=[1, *image_array.shape])
        )

        # Make prediction request and measure time
        start = time.time()
        response = await stub.Predict(request)
        prediction = response.outputs['fc_out']
        end = time.time()

        prediction_array = tf.make_ndarray(prediction)
        prediction_list = prediction_array.flatten()
        print("Inference time: ", end - start)
        # print("Prediction: ", prediction_list)

        responser = PredictorResponse(self.classes, prediction_list)
        return responser.get_response()


    async def predict(self, img):
        headers = {"content-type": "application/json"}
        # image_array = np.array(face)
        image_array = tf.keras.preprocessing.image.img_to_array(img)
        image_array = image_array.astype("float32")
        # Convert the numpy array to a JSON string
        data = json.dumps(
            {"signature_name": "serving_default", "instances": image_array.tolist()}
        )
        async with aiohttp.ClientSession() as session:
            url = "http://" + self.host + f":{self.rest_port}" + self.path
            print(url)
            async with session.post(url, data=data, headers=headers) as response:
                text = await response.text()
                # print("text", text)
                prediction = json.loads(text)["predictions"][0]
                print("REST prediction: ", prediction)
        responser = PredictorResponse(self.classes, prediction)
        return responser.get_response()

    # async def inference(self, img) -> Response:
    #     # Convert image to numpy array
    #     img = img.resize((224, 224), resample=Image.BILINEAR)
    #     headers = {"content-type": "application/json"}
    #     image_array = np.array(img)
    #     image_array = image_array.astype("float32")
    #     # Convert the numpy array to a JSON string
    #     data = json.dumps(
    #         {"signature_name": "serving_default", "instances": image_array.tolist()}
    #     )
    #     async with aiohttp.ClientSession() as session:
    #         async with session.post(self.host + f":{self.rest_port}" + self.path, data=data, headers=headers) as response:
    #             prediction = json.loads(await response.text())["predictions"][0]
    #     responser = PredictorResponse(self.classes, prediction)
    #     return responser.get_response()

    
