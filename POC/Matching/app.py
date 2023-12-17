import re
import inspect
import datetime
import aiohttp
import time
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
from fastapi.routing import APIRoute
from fastapi.openapi.utils import get_openapi
from dynaconf import settings
from elasticsearch import Elasticsearch
from fastapi.middleware.cors import CORSMiddleware

esClient = Elasticsearch(settings.ELASTIC_SEARCH_ENDPOINT)

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


class Settings(BaseModel):
    authjwt_secret_key: str = "secret"


@AuthJWT.load_config
def get_config():
    return Settings()


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Matching API",
        version="1.0",
        description="Matching API with security",
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


@app.post("/login")
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


@app.post("/refresh")
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


def get_user_feature(user_id):
    query_body = {"query": {"match": {"item_id": str(user_id)}}}
    result = esClient.search(index="features", body=query_body)
    if len(result["hits"]["hits"]) == 0:
        return None
    else:
        return result["hits"]["hits"][0]["_source"]


async def retrieval_task(payload, id_genre):
    try:
        url = (
            settings.RETRIEVAL_FEMALE_ENDPOINT
            if int(id_genre) == 1
            else settings.RETRIEVAL_MALE_ENDPOINT
        )
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                pred = await resp.json()
                print("pred", pred)
                candidates = pred["predictions"][0]["output_2"]
                scores = pred["predictions"][0]["output_1"]
                if candidates is None:
                    return [], []
                return candidates, scores
    except Exception as e:
        print("Error retrieval:", e)
        return [], []


async def ranking_task(user_id, candidates):
    try:
        url = settings.RANKING_ENDPOINT
        result = []
        instances = []
        start_candidate = time.time()
        user_feature = get_user_feature(user_id)
        for candidate in candidates:
            candidate_feature = get_user_feature(candidate)
            if candidate_feature is not None:
                instances.append(
                    {
                        "user_id": str(user_id),
                        "item_id": str(candidate),
                        "age": str(user_feature.get("age", "18")),
                        "y_age": str(candidate_feature.get("age", "18")),
                        "size": int(user_feature.get("size", "170")),
                        "y_size": int(candidate_feature.get("size", "170")),
                        "is_pratiquant": str(user_feature.get("is_pratiquant", "99")),
                        "y_is_pratiquant": str(
                            candidate_feature.get("is_pratiquant", "99")
                        ),
                        "id_genre": str(user_feature["id_genre"]),
                        "y_id_genre": str(candidate_feature["id_genre"]),
                        "on_mektoube_for": str(
                            user_feature.get("on_mektoube_for", "99")
                        ),
                        "y_on_mektoube_for": str(
                            candidate_feature.get("on_mektoube_for", "99")
                        ),
                        "job": str(user_feature.get("job", "99")),
                        "y_job": str(candidate_feature.get("job", "99")),
                        "has_children": str(user_feature.get("has_children", "99")),
                        "y_has_children": str(
                            candidate_feature.get("has_children", "99")
                        ),
                        "family_situation": str(
                            user_feature.get("family_situation", "99")
                        ),
                        "y_family_situation": str(
                            candidate_feature.get("family_situation", "99")
                        ),
                        "want_children": str(user_feature.get("want_children", "99")),
                        "y_want_children": str(
                            candidate_feature.get("want_children", "99")
                        ),
                        "birth_sign": str(user_feature.get("birth_sign", "99")),
                        "y_birth_sign": str(candidate_feature.get("birth_sign", "99")),
                    }
                )
        payload = {"instances": instances}
        end_candidate = time.time()
        print("candidate time: %s", end_candidate - start_candidate)
        # logging.info("payload: %s", payload)
        async with aiohttp.ClientSession() as session:
            start_req = time.time()
            async with session.post(url, json=payload) as resp:
                pred = await resp.json()
                print("ranking res.json(): %s", pred)

            end_req = time.time()
            print("req time: %s", end_req - start_req)
            for candidate in candidates:
                result.append(
                    {
                        "candidate_id": candidate,
                        "score": pred["predictions"][candidates.index(candidate)][0],
                    }
                )
            result = sorted(result, key=lambda d: d["score"], reverse=True)

            return result
    except Exception as e:
        print("Error ranking:", e)
        return []


@app.get("/recommend/{user_id}", operation_id="authorize")
async def recommend(user_id: int, Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    # current_user = Authorize.get_jwt_subject()
    user_row = get_user_feature(user_id)
    if user_row is None:
        raise HTTPException(status_code=404, detail="User not found")
    payload = {
        "instances": [
            {
                "user_id": str(user_id),
                "size": int(user_row["size"]),
                "age": str(user_row["age"]),
                "is_pratiquant": str(user_row.get("is_pratiquant", "99")),
                # "id_genre": str(id_genre),
                "on_mektoube_for": str(user_row.get("on_mektoube_for", "99")),
                # "job": str(job),
                "has_children": str(user_row.get("has_children", "99")),
                # "want_children": str(want_children),
                "family_situation": str(user_row.get("family_situation", "99")),
                # "birth_sign": str(birth_sign),
            }
        ]
    }

    candidates, _ = await retrieval_task(payload, int(user_row["id_genre"]))
    recommendation = await ranking_task(user_id, list(candidates))
    return recommendation
