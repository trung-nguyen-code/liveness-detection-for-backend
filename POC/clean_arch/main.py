import logging
import numpy as np
from urllib.request import Request, urlopen
from logging import config
import re
import inspect
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from handlers.handler_liveness import handler_detect_response
from usecases.image_processing import UsecaseImageProcessing


# from constants.settings import settings
from downloader import download_folder
from routers import liveness_detection_router



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
   _app = FastAPI(title="Liveness")

   _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in []],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

   return _app


app = get_application()
app.openapi = custom_openapi

app.include_router(liveness_detection_router)


    
    