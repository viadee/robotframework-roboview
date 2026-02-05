import anyio
import pytest
import logging

from types import SimpleNamespace
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import Response

import roboview.main as main_module


def _make_fake_settings():
    return SimpleNamespace(
        ENVIRONMENT="test",
        LOG_LEVEL="INFO",
        PROJECT_NAME="RoboViewTest",
        APP_VERSION="0.1.0",
        BACKEND_CORS_ORIGINS=["http://example.com"],
        HTTP_METHODS=["GET", "POST"],
        API_VERSION_STR="/api",
    )


def test_lifespan_logs_startup_and_shutdown(monkeypatch, caplog):
    fake_settings = _make_fake_settings()
    monkeypatch.setattr(main_module, "settings", fake_settings)

    caplog.set_level(logging.INFO)

    app = FastAPI(lifespan=main_module.lifespan)

    async def run_lifespan():
        async with main_module.lifespan(app):
            pass

    anyio.run(run_lifespan)

    assert "Starting application in test environment" in caplog.text
    assert "Log level set to INFO" in caplog.text
    assert "Shutting down application" in caplog.text


@pytest.mark.anyio
async def test_catch_exceptions_middleware_pass_through_asyncio(caplog):
    caplog.set_level(logging.ERROR)

    scope = {"type": "http", "method": "GET", "path": "/"}
    request = Request(scope)

    async def ok_call_next(req):
        return Response("ok", status_code=200)

    response = await main_module.catch_exceptions_middleware(request, ok_call_next)

    assert response.status_code == 200
    assert response.body == b"ok"
    assert "Internal server error" not in caplog.text


@pytest.mark.anyio
async def test_catch_exceptions_middleware_handles_exception_asyncio(caplog):
    caplog.set_level(logging.ERROR)

    scope = {"type": "http", "method": "GET", "path": "/"}
    request = Request(scope)

    async def failing_call_next(req):
        raise RuntimeError("boom")

    response = await main_module.catch_exceptions_middleware(request, failing_call_next)

    assert response.status_code == 500
    assert response.body == b"Internal server error"
    assert "Internal server error: boom" in caplog.text


def test_app_is_configured_with_middlewares_and_router(monkeypatch):
    fake_settings = _make_fake_settings()
    monkeypatch.setattr(main_module, "settings", fake_settings, raising=False)

    fake_router = APIRouter()

    @fake_router.get("/ping")
    def ping():
        return {"status": "ok"}

    monkeypatch.setattr(main_module, "api_router", fake_router, raising=False)

    app = FastAPI(
        title=fake_settings.PROJECT_NAME,
        lifespan=main_module.lifespan,
        version=fake_settings.APP_VERSION,
    )
    app.middleware("http")(main_module.catch_exceptions_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(o) for o in fake_settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=[str(o) for o in fake_settings.HTTP_METHODS],
        allow_headers=["*"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.include_router(fake_router, prefix=fake_settings.API_VERSION_STR)

    middleware_classes = {m.cls for m in app.user_middleware}
    assert GZipMiddleware in middleware_classes
    assert any("CORSMiddleware" in m.cls.__name__ for m in app.user_middleware)

    paths = {route.path for route in app.router.routes}
    assert f"{fake_settings.API_VERSION_STR}/ping" in paths