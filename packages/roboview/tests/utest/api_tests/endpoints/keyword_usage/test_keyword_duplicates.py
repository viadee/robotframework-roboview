import asyncio
import logging
from typing import Any, Dict

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from roboview.api.endpoints.keyword_usage.keyword_duplicates import (
    router,
    get_potential_duplicate_keywords,
    logger,
)
from roboview.schemas.dtos.keyword_similarity import DuplicateKeywordResponse


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/keyword-duplicates")

    class FakeKeywordUsageService:
        def __init__(self) -> None:
            self.called_with_similarity_service = None

        def get_potential_duplicate_keywords(self, keyword_similarity_service):
            self.called_with_similarity_service = keyword_similarity_service
            return [
                {
                    "keyword_id": "k1",
                    "file_name": "file1.robot",
                    "keyword_name_without_prefix": "Login User",
                    "keyword_name_with_prefix": "MyLib.Login User",
                    "source": "MyLib",
                    "file_usages": 3,
                    "total_usages": 5,
                },
                {
                    "keyword_id": "k2",
                    "file_name": "file2.robot",
                    "keyword_name_without_prefix": "Open Browser",
                    "keyword_name_with_prefix": "MyLib.Open Browser",
                    "source": "MyLib",
                    "file_usages": 2,
                    "total_usages": 4,
                },
            ]

    class FakeKeywordSimilarityService:
        pass

    app.state.keyword_usage_service = FakeKeywordUsageService()
    app.state.keyword_similarity_service = FakeKeywordSimilarityService()
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_get_potential_duplicate_keywords_happy_path_direct(test_app: FastAPI):
    scope: Dict[str, Any] = {"type": "http", "app": test_app}
    request = Request(scope=scope)

    result: DuplicateKeywordResponse = asyncio.run(
        get_potential_duplicate_keywords(request=request)
    )

    assert isinstance(result, DuplicateKeywordResponse)
    assert len(result.duplicate_keywords) == 2
    assert result.duplicate_keywords[0].keyword_id == "k1"
    assert result.duplicate_keywords[1].keyword_id == "k2"


def test_get_potential_duplicate_keywords_happy_path(client: TestClient, test_app: FastAPI):
    response = client.get("/keyword-duplicates")
    assert response.status_code == 200

    body = response.json()
    parsed = DuplicateKeywordResponse(**body)

    assert isinstance(parsed, DuplicateKeywordResponse)
    assert len(parsed.duplicate_keywords) == 2

    first = parsed.duplicate_keywords[0]
    second = parsed.duplicate_keywords[1]

    assert first.keyword_id == "k1"
    assert first.file_name == "file1.robot"
    assert first.keyword_name_without_prefix == "Login User"
    assert first.keyword_name_with_prefix == "MyLib.Login User"
    assert first.source == "MyLib"
    assert first.file_usages == 3
    assert first.total_usages == 5

    assert second.keyword_id == "k2"
    assert second.file_name == "file2.robot"
    assert second.keyword_name_without_prefix == "Open Browser"
    assert second.keyword_name_with_prefix == "MyLib.Open Browser"
    assert second.source == "MyLib"
    assert second.file_usages == 2
    assert second.total_usages == 4

    usage_service = test_app.state.keyword_usage_service
    similarity_service = test_app.state.keyword_similarity_service
    assert usage_service.called_with_similarity_service is similarity_service


def test_get_potential_duplicate_keywords_empty_list(client: TestClient, test_app: FastAPI, monkeypatch):
    def _empty_return(_):
        return []

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_potential_duplicate_keywords",
        _empty_return,
    )

    response = client.get("/keyword-duplicates")
    assert response.status_code == 200

    body = response.json()
    parsed = DuplicateKeywordResponse(**body)
    assert parsed.duplicate_keywords == []


def test_get_potential_duplicate_keywords_internal_error(client: TestClient, test_app: FastAPI, monkeypatch, caplog):
    def _raise_error(_):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_potential_duplicate_keywords",
        _raise_error,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    response = client.get("/keyword-duplicates")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert any(
        "Error retrieving potential duplicate keywords" in record.getMessage()
        for record in caplog.records
    )