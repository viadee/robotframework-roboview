"""Main entry point for the RoboView backend."""

import logging
from collections.abc import Callable
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from roboview.api.endpoints import api_router
from roboview.core.config import get_settings
from roboview.core.logging import setup_logging
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Settings
settings = get_settings()

# Setup logging on startup
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001, ANN201
    """FastAPI lifespan context manager."""
    # Startup logs
    logger.info("Starting application in %s environment", settings.ENVIRONMENT)
    logger.info("Log level set to %s", settings.LOG_LEVEL)
    logger.debug("Debug logging is enabled")

    yield

    # Shutdown logs
    logger.info("Shutting down application")


async def catch_exceptions_middleware(request: Request, call_next: Callable) -> Response:
    """Catch exceptions and handle them.

    Configured this way so the CORS middleware can catch exceptions and still return
    the appropriate headers.

    See https://github.com/fastapi/fastapi/issues/775#issuecomment-592946834.
    """
    try:
        return await call_next(request)
    except Exception as e:
        msg = f"Internal server error: {e}"
        logger.exception(msg)
        return Response("Internal server error", status_code=500)


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan, version=settings.APP_VERSION)

app.middleware("http")(catch_exceptions_middleware)
# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(o) for o in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=[str(o) for o in settings.HTTP_METHODS],
    allow_headers=["*"],
)
# Enable GZip compression (useful since we're returning images in base64)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Routes
app.include_router(api_router, prefix=settings.API_VERSION_STR)

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level=settings.LOG_LEVEL.lower(),
    )
