import asyncio
import logging

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from roboview.api.endpoints.system.health import (
    router,
    health_check,
    logger,
)
from roboview.schemas.dtos.common import HealthCheck


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/health")
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_health_check_happy_path_direct(test_app: FastAPI, caplog):
    caplog.set_level(logging.INFO, logger=logger.name)

    result: HealthCheck = asyncio.run(health_check())

    assert isinstance(result, HealthCheck)
    assert result.status == "ok"
    assert any("Health check requested" in record.getMessage() for record in caplog.records)


def test_health_check_happy_path_endpoint(client: TestClient, caplog):
    caplog.set_level(logging.INFO, logger=logger.name)

    response = client.get("/health")
    assert response.status_code == 200

    body = response.json()
    parsed = HealthCheck(**body)

    assert isinstance(parsed, HealthCheck)
    assert parsed.status == "ok"
    assert any("Health check requested" in record.getMessage() for record in caplog.records)