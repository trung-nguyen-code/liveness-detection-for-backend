import logging
from logging import config
import re
import inspect
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware


from app.routers.users import user_router, user_jobs_router
from app.routers.you_profiles import you_profile_router
from app.routers.settings import router as settings_router
from app.constants.settings import settings

config.fileConfig("logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

app = FastAPI()


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
app.include_router(user_router)
app.include_router(user_jobs_router)

# you profile route
app.include_router(you_profile_router)

# setting route
app.include_router(settings_router)
