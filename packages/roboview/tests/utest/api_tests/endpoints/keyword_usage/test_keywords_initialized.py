import asyncio
import logging
from pathlib import Path
from typing import Any, Dict

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from roboview.api.endpoints.keyword_usage.keywords_initialized import (
    router,
    get_init_keywords,
    logger,
)
from roboview.schemas.domain.common import KeywordType
from roboview.schemas.dtos.keyword_usage import InitializedKeywordsResponse


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/keywords-initialized")

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
                    "file_name": "resource1.resource",
                    "keyword_name_without_prefix": "Setup Environment",
                    "keyword_name_with_prefix": "Res.Setup Environment",
                    "source": "Res",
                    "file_usages": 2,
                    "total_usages": 4,
                },
                {
                    "keyword_id": "k2",
                    "file_name": "resource1.resource",
                    "keyword_name_without_prefix": "Init Browser",
                    "keyword_name_with_prefix": "Res.Init Browser",
                    "source": "Res",
                    "file_usages": 1,
                    "total_usages": 1,
                },
            ]

    app.state.keyword_usage_service = FakeKeywordUsageService()
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_get_init_keywords_happy_path_direct(test_app: FastAPI):
    scope: Dict[str, Any] = {"type": "http", "app": test_app}
    request = Request(scope=scope)
    file_path = Path("/path/to/project/resources/resource1.resource")

    result: InitializedKeywordsResponse = asyncio.run(
        get_init_keywords(request=request, file_path=file_path)
    )

    assert isinstance(result, InitializedKeywordsResponse)
    assert len(result.initialized_keywords) == 2

    first = result.initialized_keywords[0]
    assert first.keyword_id == "k1"
    assert first.file_name == "resource1.resource"
    assert first.keyword_name_without_prefix == "Setup Environment"
    assert first.keyword_name_with_prefix == "Res.Setup Environment"
    assert first.source == "Res"
    assert first.file_usages == 2
    assert first.total_usages == 4

    service = test_app.state.keyword_usage_service
    assert service.called_with_file_path == file_path
    assert service.called_with_keyword_type is KeywordType.INITIALIZED


def test_get_init_keywords_happy_path(client: TestClient, test_app: FastAPI):
    file_path = "/path/to/project/resources/resource1.resource"

    response = client.get(
        "/keywords-initialized",
        params={"file_path": file_path},
    )
    assert response.status_code == 200

    body = response.json()
    parsed = InitializedKeywordsResponse(**body)

    assert isinstance(parsed, InitializedKeywordsResponse)
    assert len(parsed.initialized_keywords) == 2

    first = parsed.initialized_keywords[0]
    assert first.keyword_id == "k1"
    assert first.file_name == "resource1.resource"
    assert first.keyword_name_without_prefix == "Setup Environment"
    assert first.keyword_name_with_prefix == "Res.Setup Environment"
    assert first.source == "Res"
    assert first.file_usages == 2
    assert first.total_usages == 4

    service = test_app.state.keyword_usage_service
    assert service.called_with_file_path == Path(file_path)
    assert service.called_with_keyword_type is KeywordType.INITIALIZED


def test_get_init_keywords_empty_result(client: TestClient, test_app: FastAPI, monkeypatch):
    def _empty_return(file_path: Path, keyword_type: KeywordType):
        return []

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_keywords_with_global_usage_for_file",
        _empty_return,
    )

    response = client.get(
        "/keywords-initialized",
        params={"file_path": "/path/to/project/resources/resource1.resource"},
    )
    assert response.status_code == 200

    body = response.json()
    parsed = InitializedKeywordsResponse(**body)
    assert parsed.initialized_keywords == []


def test_get_init_keywords_internal_error(client: TestClient, test_app: FastAPI, monkeypatch, caplog):
    def _raise_error(file_path: Path, keyword_type: KeywordType):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_keywords_with_global_usage_for_file",
        _raise_error,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    response = client.get(
        "/keywords-initialized",
        params={"file_path": "/path/to/project/resources/resource1.resource"},
    )
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert any(
        "Error fetching init keywords for resource" in record.getMessage()
        for record in caplog.records
    )