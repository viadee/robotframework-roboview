import asyncio
import logging
from pathlib import Path
from typing import Any, Dict

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from roboview.api.endpoints.keyword_usage.keywords_called import (
    router,
    get_called_keywords,
    logger,
)
from roboview.schemas.domain.common import KeywordType
from roboview.schemas.dtos.keyword_usage import CalledKeywordsResponse


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/keywords-called")

    class FakeKeywordUsageService:
        def __init__(self) -> None:
            self.called_with_file_path: Path | None = None
            self.called_with_keyword_type: KeywordType | None = None

        def get_keywords_with_global_usage_for_file(self, file_path: Path, keyword_type: KeywordType):
            self.called_with_file_path = file_path
            self.called_with_keyword_type = keyword_type
            return [
                {
                    "keyword_id": "k1",
                    "file_name": "test1.robot",
                    "keyword_name_without_prefix": "Login User",
                    "keyword_name_with_prefix": "MyLib.Login User",
                    "source": "MyLib",
                    "file_usages": 3,
                    "total_usages": 5,
                },
                {
                    "keyword_id": "k2",
                    "file_name": "test1.robot",
                    "keyword_name_without_prefix": "Open Browser",
                    "keyword_name_with_prefix": "MyLib.Open Browser",
                    "source": "MyLib",
                    "file_usages": 1,
                    "total_usages": 2,
                },
            ]

    app.state.keyword_usage_service = FakeKeywordUsageService()
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_get_called_keywords_happy_path_direct(test_app: FastAPI):
    scope: Dict[str, Any] = {"type": "http", "app": test_app}
    request = Request(scope=scope)
    file_path = Path("/path/to/project/tests/test1.robot")

    result: CalledKeywordsResponse = asyncio.run(
        get_called_keywords(request=request, file_path=file_path)
    )

    assert isinstance(result, CalledKeywordsResponse)
    assert len(result.called_keywords) == 2

    first = result.called_keywords[0]
    assert first.keyword_id == "k1"
    assert first.file_name == "test1.robot"
    assert first.keyword_name_without_prefix == "Login User"
    assert first.keyword_name_with_prefix == "MyLib.Login User"
    assert first.source == "MyLib"
    assert first.file_usages == 3
    assert first.total_usages == 5

    service = test_app.state.keyword_usage_service
    assert service.called_with_file_path == file_path
    assert service.called_with_keyword_type is KeywordType.CALLED


def test_get_called_keywords_happy_path(client: TestClient, test_app: FastAPI):
    file_path = "/path/to/project/tests/test1.robot"

    response = client.get(
        "/keywords-called",
        params={"file_path": file_path},
    )
    assert response.status_code == 200

    body = response.json()
    parsed = CalledKeywordsResponse(**body)

    assert isinstance(parsed, CalledKeywordsResponse)
    assert len(parsed.called_keywords) == 2

    first = parsed.called_keywords[0]
    assert first.keyword_id == "k1"
    assert first.file_name == "test1.robot"
    assert first.keyword_name_without_prefix == "Login User"
    assert first.keyword_name_with_prefix == "MyLib.Login User"
    assert first.source == "MyLib"
    assert first.file_usages == 3
    assert first.total_usages == 5

    service = test_app.state.keyword_usage_service
    assert service.called_with_file_path == Path(file_path)
    assert service.called_with_keyword_type is KeywordType.CALLED


def test_get_called_keywords_empty_result(client: TestClient, test_app: FastAPI, monkeypatch):
    def _empty_return(file_path: Path, keyword_type: KeywordType):
        return []

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_keywords_with_global_usage_for_file",
        _empty_return,
    )

    response = client.get(
        "/keywords-called",
        params={"file_path": "/path/to/project/tests/test1.robot"},
    )
    assert response.status_code == 200

    body = response.json()
    parsed = CalledKeywordsResponse(**body)
    assert parsed.called_keywords == []


def test_get_called_keywords_bad_request_on_value_error(client: TestClient, test_app: FastAPI, monkeypatch, caplog):
    def _raise_value_error(file_path: Path, keyword_type: KeywordType):
        raise ValueError("invalid file type")

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_keywords_with_global_usage_for_file",
        _raise_value_error,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    response = client.get(
        "/keywords-called",
        params={"file_path": "/path/to/project/tests/invalid.txt"},
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "Bad Request"}
    assert any(
        "Invalid file type. Must be .robot or .resource" in record.getMessage()
        for record in caplog.records
    )


def test_get_called_keywords_internal_error(client: TestClient, test_app: FastAPI, monkeypatch, caplog):
    def _raise_error(file_path: Path, keyword_type: KeywordType):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_keywords_with_global_usage_for_file",
        _raise_error,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    response = client.get(
        "/keywords-called",
        params={"file_path": "/path/to/project/tests/test1.robot"},
    )
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert any(
        "Error fetching called keywords for file" in record.getMessage()
        for record in caplog.records
    )