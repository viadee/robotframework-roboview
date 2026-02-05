import asyncio
import logging
from typing import Any, Dict

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from roboview.api.endpoints.keyword_usage.keywords_wo_usages import (
    router,
    get_keywords_wo_usages,
    logger,
)
from roboview.schemas.dtos.keyword_usage import KeywordsWithoutUsagesResponse


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/keywords-wo-usages")

    class FakeKeywordUsageService:
        def __init__(self) -> None:
            self.called = False

        def get_keywords_without_usages(self):
            self.called = True
            return [
                {
                    "keyword_id": "k1",
                    "file_name": "resource1.resource",
                    "keyword_name_without_prefix": "Setup Environment",
                    "keyword_name_with_prefix": "Res.Setup Environment",
                    "source": "Res",
                    "file_usages": 0,
                    "total_usages": 0,
                },
                {
                    "keyword_id": "k2",
                    "file_name": "test1.robot",
                    "keyword_name_without_prefix": "Login User",
                    "keyword_name_with_prefix": "Tests.Login User",
                    "source": "Tests",
                    "file_usages": 0,
                    "total_usages": 0,
                },
            ]

    app.state.keyword_usage_service = FakeKeywordUsageService()
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_get_keywords_wo_usages_happy_path_direct(test_app: FastAPI):
    scope: Dict[str, Any] = {"type": "http", "app": test_app}
    request = Request(scope=scope)

    result: KeywordsWithoutUsagesResponse = asyncio.run(
        get_keywords_wo_usages(request=request)
    )

    assert isinstance(result, KeywordsWithoutUsagesResponse)
    assert len(result.keywords_wo_usages) == 2

    first = result.keywords_wo_usages[0]
    assert first.keyword_id == "k1"
    assert first.file_name == "resource1.resource"
    assert first.keyword_name_without_prefix == "Setup Environment"
    assert first.keyword_name_with_prefix == "Res.Setup Environment"
    assert first.source == "Res"
    assert first.file_usages == 0
    assert first.total_usages == 0

    service = test_app.state.keyword_usage_service
    assert service.called is True


def test_get_keywords_wo_usages_happy_path(client: TestClient, test_app: FastAPI):
    response = client.get("/keywords-wo-usages")
    assert response.status_code == 200

    body = response.json()
    parsed = KeywordsWithoutUsagesResponse(**body)

    assert isinstance(parsed, KeywordsWithoutUsagesResponse)
    assert len(parsed.keywords_wo_usages) == 2

    first = parsed.keywords_wo_usages[0]
    assert first.keyword_id == "k1"
    assert first.file_name == "resource1.resource"
    assert first.keyword_name_without_prefix == "Setup Environment"
    assert first.keyword_name_with_prefix == "Res.Setup Environment"
    assert first.source == "Res"
    assert first.file_usages == 0
    assert first.total_usages == 0

    service = test_app.state.keyword_usage_service
    assert service.called is True


def test_get_keywords_wo_usages_empty_result(client: TestClient, test_app: FastAPI, monkeypatch):
    def _empty_return():
        return []

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_keywords_without_usages",
        _empty_return,
    )

    response = client.get("/keywords-wo-usages")
    assert response.status_code == 200

    body = response.json()
    parsed = KeywordsWithoutUsagesResponse(**body)
    assert parsed.keywords_wo_usages == []


def test_get_keywords_wo_usages_internal_error(client: TestClient, test_app: FastAPI, monkeypatch, caplog):
    def _raise_error():
        raise RuntimeError("boom")

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_keywords_without_usages",
        _raise_error,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    response = client.get("/keywords-wo-usages")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert any(
        "Error retrieving keywords without usages." in record.getMessage()
        for record in caplog.records
    )