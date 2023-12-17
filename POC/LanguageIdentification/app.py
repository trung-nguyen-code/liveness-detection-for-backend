import re
import inspect
import datetime
import time
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from fastapi.routing import APIRoute
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from model import LanguageIdentification
from googletrans import Translator


language_model = LanguageIdentification()
translator = Translator()

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
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(BaseModel):
    username: str
    password: str


class JWTSettings(BaseModel):
    authjwt_secret_key: str = "secret"


@AuthJWT.load_config
def get_config():
    return JWTSettings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Language API",
        version="1.0",
        description="Language API with security",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token",
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


app.openapi = custom_openapi


@app.post("/login", tags=["Auth"])
def login(user: User, Authorize: AuthJWT = Depends()):
    if user.username != "test" or user.password != "test":
        raise HTTPException(status_code=401, detail="Bad username or password")

    # Use create_access_token() and create_refresh_token() to create our
    # access and refresh tokens
    expires = datetime.timedelta(days=1)
    access_token = Authorize.create_access_token(
        subject=user.username, expires_time=False
    )
    refresh_token = Authorize.create_refresh_token(subject=user.username)
    return {"access_token": access_token, "refresh_token": refresh_token}


@app.post("/refresh", tags=["Auth"])
def refresh(Authorize: AuthJWT = Depends()):
    """
    The jwt_refresh_token_required() function insures a valid refresh
    token is present in the request before running any code below that function.
    we can use the get_jwt_subject() function to get the subject of the refresh
    token, and use the create_access_token() function again to make a new access token
    """
    Authorize.jwt_refresh_token_required()

    current_user = Authorize.get_jwt_subject()
    expires = datetime.timedelta(days=1)
    new_access_token = Authorize.create_access_token(
        subject=current_user, expires_time=expires
    )
    return {"access_token": new_access_token}


@app.post("/detect", tags=["Dectection"])
async def detect(text: str, Authorize: AuthJWT = Depends()):
    # Authorize.jwt_required()

    start = time.time()
    labels, probs = language_model.predict_lang(text)
    end = time.time()

    print("Time taken to detect language: ", end - start)
    return {
        "code": labels[0].replace("__label__", ""),
        "probability": probs[0],
    }


@app.post("/detect_then_translate", tags=["Dectection"])
async def detect_then_translate(text: str, Authorize: AuthJWT = Depends()):
    # Authorize.jwt_required()

    start = time.time()
    labels, _ = language_model.predict_lang(text)
    end = time.time()
    src_language = labels[0].replace("__label__", "")

    print("Time taken to detect language: ", end - start)

    start_translate = time.time()
    translated = translator.translate(text, dest="fr", src=src_language)
    end_translate = time.time()
    print("Time taken to translate: ", end_translate - start_translate)

    return {
        "translated": translated.text,
    }
