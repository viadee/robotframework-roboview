import asyncio
import logging
from typing import Any, Dict, List

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from roboview.api.endpoints.robocop.robocop_messages import (
    router,
    get_robocop_messages,
    logger,
)
from roboview.schemas.dtos.robocop import RobocopMessagesResponse


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/robocop-messages")

    class FakeRobocopService:
        def __init__(self) -> None:
            self.called = False

        def get_robocop_error_messages(self) -> List[dict]:
            self.called = True
            return [
                {
                    "message_id": "m1",
                    "rule_id": "E0101",
                    "rule_message": "First issue",
                    "message": "First issue",
                    "category": "ERROR",
                    "file_name": "file1.robot",
                    "source": "/path/to/file1.robot",
                    "severity": "ERROR",
                    "code": "E0101",
                    "path": "/path/to/file1.robot",
                    "line": 10,
                    "column": 3,
                    "rule_name": "first-rule",
                    "description": "First issue description",
                },
                {
                    "message_id": "m2",
                    "rule_id": "W0202",
                    "rule_message": "Second issue",
                    "message": "Second issue",
                    "category": "WARNING",
                    "file_name": "file2.robot",
                    "source": "/path/to/file2.robot",
                    "severity": "WARNING",
                    "code": "W0202",
                    "path": "/path/to/file2.robot",
                    "line": 20,
                    "column": 5,
                    "rule_name": "second-rule",
                    "description": "Second issue description",
                },
            ]

    app.state.robocop_service = FakeRobocopService()
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_get_robocop_messages_happy_path_direct(test_app: FastAPI):
    scope: Dict[str, Any] = {"type": "http", "app": test_app}
    request = Request(scope=scope)

    result: RobocopMessagesResponse = asyncio.run(
        get_robocop_messages(request=request)
    )

    assert isinstance(result, RobocopMessagesResponse)
    assert len(result.messages) == 2

    first = result.messages[0]
    assert first.message_id == "m1"
    assert first.rule_id == "E0101"
    assert first.rule_message == "First issue"
    assert first.message == "First issue"
    assert first.category == "ERROR"
    assert first.file_name == "file1.robot"
    assert first.source == "/path/to/file1.robot"
    assert first.severity == "ERROR"
    assert first.code == "E0101"

    service = test_app.state.robocop_service
    assert service.called is True


def test_get_robocop_messages_happy_path_endpoint(client: TestClient, test_app: FastAPI):
    response = client.get("/robocop-messages")
    assert response.status_code == 200

    body = response.json()
    parsed = RobocopMessagesResponse(**body)

    assert isinstance(parsed, RobocopMessagesResponse)
    assert len(parsed.messages) == 2

    first = parsed.messages[0]
    assert first.message_id == "m1"
    assert first.rule_id == "E0101"
    assert first.rule_message == "First issue"
    assert first.message == "First issue"
    assert first.category == "ERROR"
    assert first.file_name == "file1.robot"
    assert first.source == "/path/to/file1.robot"
    assert first.severity == "ERROR"
    assert first.code == "E0101"

    service = test_app.state.robocop_service
    assert service.called is True


def test_get_robocop_messages_empty_result(client: TestClient, test_app: FastAPI, monkeypatch):
    def _empty_return() -> List[dict]:
        return []

    monkeypatch.setattr(
        test_app.state.robocop_service,
        "get_robocop_error_messages",
        _empty_return,
    )

    response = client.get("/robocop-messages")
    assert response.status_code == 200

    body = response.json()
    parsed = RobocopMessagesResponse(**body)
    assert parsed.messages == []


def test_get_robocop_messages_internal_error(client: TestClient, test_app: FastAPI, monkeypatch, caplog):
    def _raise_error() -> List[dict]:
        raise RuntimeError("boom")

    monkeypatch.setattr(
        test_app.state.robocop_service,
        "get_robocop_error_messages",
        _raise_error,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    response = client.get("/robocop-messages")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert any(
        "Error retrieving keywords without usages." in record.getMessage()
        for record in caplog.records
    )