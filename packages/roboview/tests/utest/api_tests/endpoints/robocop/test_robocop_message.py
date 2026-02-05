import asyncio
import logging
from typing import Any, Dict

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from roboview.api.endpoints.robocop.robocop_message import (
    router,
    get_robocop_message,
    logger,
)
from roboview.schemas.dtos.robocop import RobocopMessageResponse


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/robocop-message")

    class FakeRobocopService:
        def __init__(self) -> None:
            self.last_id: str | None = None

        def get_robocop_message_by_id(self, message_uuid: str) -> dict:
            self.last_id = message_uuid
            return {
                "message_id": message_uuid,
                "rule_id": "E0101",
                "rule_message": "Something is wrong",
                "message": "Something is wrong",
                "category": "ERROR",
                "file_name": "file.robot",
                "source": "/path/to/file.robot",
                "severity": "ERROR",
                "code": "E0101",
                "path": "/path/to/file.robot",
                "line": 42,
                "column": 5,
                "rule_name": "some-rule",
                "description": "Something is wrong",
            }

    app.state.robocop_service = FakeRobocopService()
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_get_robocop_message_happy_path_direct(test_app: FastAPI):
    scope: Dict[str, Any] = {"type": "http", "app": test_app}
    request = Request(scope=scope)
    msg_id = "abc-123"

    result: RobocopMessageResponse = asyncio.run(
        get_robocop_message(request=request, message_uuid=msg_id)
    )

    assert isinstance(result, RobocopMessageResponse)
    assert result.message.message_id == msg_id
    assert result.message.rule_id == "E0101"
    assert result.message.rule_message == "Something is wrong"
    assert result.message.message == "Something is wrong"
    assert result.message.category == "ERROR"
    assert result.message.file_name == "file.robot"
    assert result.message.source == "/path/to/file.robot"
    assert result.message.severity == "ERROR"
    assert result.message.code == "E0101"

    service = test_app.state.robocop_service
    assert service.last_id == msg_id


def test_get_robocop_message_happy_path_endpoint(client: TestClient, test_app: FastAPI):
    msg_id = "abc-123"

    response = client.get("/robocop-message", params={"message_uuid": msg_id})
    assert response.status_code == 200

    body = response.json()
    parsed = RobocopMessageResponse(**body)

    assert isinstance(parsed, RobocopMessageResponse)
    assert parsed.message.message_id == msg_id
    assert parsed.message.rule_id == "E0101"
    assert parsed.message.rule_message == "Something is wrong"
    assert parsed.message.message == "Something is wrong"
    assert parsed.message.category == "ERROR"
    assert parsed.message.file_name == "file.robot"
    assert parsed.message.source == "/path/to/file.robot"
    assert parsed.message.severity == "ERROR"
    assert parsed.message.code == "E0101"

    service = test_app.state.robocop_service
    assert service.last_id == msg_id


def test_get_robocop_message_internal_error(client: TestClient, test_app: FastAPI, monkeypatch, caplog):
    def _raise_error(message_uuid: str):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        test_app.state.robocop_service,
        "get_robocop_message_by_id",
        _raise_error,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    response = client.get("/robocop-message", params={"message_uuid": "abc-123"})
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert any(
        "Error retrieving keywords without usages." in record.getMessage()
        for record in caplog.records
    )