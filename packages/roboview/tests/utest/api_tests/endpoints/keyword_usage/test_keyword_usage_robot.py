import asyncio
import logging
from typing import Any, Dict

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from roboview.api.endpoints.keyword_usage.keyword_usage_robot import (
    router,
    get_kw_usage_robot,
    logger,
)
from roboview.schemas.domain.common import FileType
from roboview.schemas.dtos.keyword_usage import KeywordUsageRobotResponse


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/keyword-usage-robot")

    class FakeKeywordUsageService:
        def __init__(self) -> None:
            self.called_with_keyword_name = None
            self.called_with_file_type = None

        def get_keyword_usage_in_files_for_target_keyword(self, keyword_name: str, file_type: FileType):
            self.called_with_keyword_name = keyword_name
            self.called_with_file_type = file_type
            return [
                {
                    "file_name": "test1.robot",
                    "path": "/path/to/project/tests/test1.robot",
                    "usages": 4,
                },
                {
                    "file_name": "test2.robot",
                    "path": "/path/to/project/tests/test2.robot",
                    "usages": 2,
                },
            ]

    app.state.keyword_usage_service = FakeKeywordUsageService()
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_get_kw_usage_robot_happy_path_direct(test_app: FastAPI):
    scope: Dict[str, Any] = {"type": "http", "app": test_app}
    request = Request(scope=scope)

    result: KeywordUsageRobotResponse = asyncio.run(
        get_kw_usage_robot(request=request, keyword_name="Login User")
    )

    assert isinstance(result, KeywordUsageRobotResponse)
    assert len(result.keyword_usage_robot) == 2

    first = result.keyword_usage_robot[0]
    assert first.file_name == "test1.robot"
    assert first.path == "/path/to/project/tests/test1.robot"
    assert first.usages == 4

    service = test_app.state.keyword_usage_service
    assert service.called_with_keyword_name == "Login User"
    assert service.called_with_file_type is FileType.ROBOT


def test_get_kw_usage_robot_happy_path(client: TestClient, test_app: FastAPI):
    response = client.get(
        "/keyword-usage-robot",
        params={"keyword_name": "Login User"},
    )
    assert response.status_code == 200

    body = response.json()
    parsed = KeywordUsageRobotResponse(**body)

    assert isinstance(parsed, KeywordUsageRobotResponse)
    assert len(parsed.keyword_usage_robot) == 2

    first = parsed.keyword_usage_robot[0]
    assert first.file_name == "test1.robot"
    assert first.path == "/path/to/project/tests/test1.robot"
    assert first.usages == 4

    service = test_app.state.keyword_usage_service
    assert service.called_with_keyword_name == "Login User"
    assert service.called_with_file_type is FileType.ROBOT


def test_get_kw_usage_robot_empty_result(client: TestClient, test_app: FastAPI, monkeypatch):
    def _empty_return(keyword_name: str, file_type: FileType):
        return []

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_keyword_usage_in_files_for_target_keyword",
        _empty_return,
    )

    response = client.get(
        "/keyword-usage-robot",
        params={"keyword_name": "Login User"},
    )
    assert response.status_code == 200

    body = response.json()
    parsed = KeywordUsageRobotResponse(**body)
    assert parsed.keyword_usage_robot == []


def test_get_kw_usage_robot_internal_error(client: TestClient, test_app: FastAPI, monkeypatch, caplog):
    def _raise_error(keyword_name: str, file_type: FileType):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_keyword_usage_in_files_for_target_keyword",
        _raise_error,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    response = client.get(
        "/keyword-usage-robot",
        params={"keyword_name": "Login User"},
    )
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert any(
        "Error robot files for keyword Login User" in record.getMessage()
        for record in caplog.records
    )