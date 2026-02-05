import asyncio
import logging
from typing import Any, Dict

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from roboview.api.endpoints.keyword_usage.keywords_wo_documentation import (
    router,
    get_keywords_wo_doc,
    logger,
)
from roboview.schemas.dtos.keyword_usage import KeywordsWithoutDocResponse


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/keywords-wo-doc")

    class FakeKeywordUsageService:
        def __init__(self) -> None:
            self.called = False

        def get_keywords_without_documentation(self):
            self.called = True
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
                    "file_name": "test1.robot",
                    "keyword_name_without_prefix": "Login User",
                    "keyword_name_with_prefix": "Tests.Login User",
                    "source": "Tests",
                    "file_usages": 1,
                    "total_usages": 3,
                },
            ]

    app.state.keyword_usage_service = FakeKeywordUsageService()
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_get_keywords_wo_doc_happy_path_direct(test_app: FastAPI):
    scope: Dict[str, Any] = {"type": "http", "app": test_app}
    request = Request(scope=scope)

    result: KeywordsWithoutDocResponse = asyncio.run(
        get_keywords_wo_doc(request=request)
    )

    assert isinstance(result, KeywordsWithoutDocResponse)
    assert len(result.keywords_wo_documentation) == 2

    first = result.keywords_wo_documentation[0]
    assert first.keyword_id == "k1"
    assert first.file_name == "resource1.resource"
    assert first.keyword_name_without_prefix == "Setup Environment"
    assert first.keyword_name_with_prefix == "Res.Setup Environment"
    assert first.source == "Res"
    assert first.file_usages == 2
    assert first.total_usages == 4

    service = test_app.state.keyword_usage_service
    assert service.called is True


def test_get_keywords_wo_doc_happy_path(client: TestClient, test_app: FastAPI):
    response = client.get("/keywords-wo-doc")
    assert response.status_code == 200

    body = response.json()
    parsed = KeywordsWithoutDocResponse(**body)

    assert isinstance(parsed, KeywordsWithoutDocResponse)
    assert len(parsed.keywords_wo_documentation) == 2

    first = parsed.keywords_wo_documentation[0]
    assert first.keyword_id == "k1"
    assert first.file_name == "resource1.resource"
    assert first.keyword_name_without_prefix == "Setup Environment"
    assert first.keyword_name_with_prefix == "Res.Setup Environment"
    assert first.source == "Res"
    assert first.file_usages == 2
    assert first.total_usages == 4

    service = test_app.state.keyword_usage_service
    assert service.called is True


def test_get_keywords_wo_doc_empty_result(client: TestClient, test_app: FastAPI, monkeypatch):
    def _empty_return():
        return []

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_keywords_without_documentation",
        _empty_return,
    )

    response = client.get("/keywords-wo-doc")
    assert response.status_code == 200

    body = response.json()
    parsed = KeywordsWithoutDocResponse(**body)
    assert parsed.keywords_wo_documentation == []


def test_get_keywords_wo_doc_internal_error(client: TestClient, test_app: FastAPI, monkeypatch, caplog):
    def _raise_error():
        raise RuntimeError("boom")

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_keywords_without_documentation",
        _raise_error,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    response = client.get("/keywords-wo-doc")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert any(
        "Error retrieving keywords without documentation." in record.getMessage()
        for record in caplog.records
    )