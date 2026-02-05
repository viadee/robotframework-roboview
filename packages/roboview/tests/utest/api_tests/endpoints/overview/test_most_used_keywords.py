import asyncio
import logging
from typing import Any, Dict

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from roboview.api.endpoints.overview.most_used_keywords import (
    router,
    get_most_used_keywords,
    logger,
)
from roboview.schemas.dtos.overview import MostUsedKeywordsResponse


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/most-used-keywords")

    class FakeKeywordUsageService:
        def __init__(self) -> None:
            self.user_called_with_n: int | None = None
            self.ext_called_with_n: int | None = None

        def get_most_used_user_defined_keywords(self, n: int):
            self.user_called_with_n = n
            return [
                {
                    "keyword_id": "u1",
                    "file_name": "user1.robot",
                    "keyword_name_without_prefix": "Login User",
                    "keyword_name_with_prefix": "Suite.Login User",
                    "source": "Suite",
                    "file_usages": 5,
                    "total_usages": 10,
                },
                {
                    "keyword_id": "u2",
                    "file_name": "user2.robot",
                    "keyword_name_without_prefix": "Search",
                    "keyword_name_with_prefix": "Suite.Search",
                    "source": "Suite",
                    "file_usages": 3,
                    "total_usages": 6,
                },
            ]

        def get_most_used_external_or_builtin_keywords(self, n: int):
            self.ext_called_with_n = n
            return [
                {
                    "keyword_id": "e1",
                    "file_name": "BuiltIn",
                    "keyword_name_without_prefix": "Log",
                    "keyword_name_with_prefix": "BuiltIn.Log",
                    "source": "BuiltIn",
                    "file_usages": 8,
                    "total_usages": 15,
                },
                {
                    "keyword_id": "e2",
                    "file_name": "SeleniumLibrary",
                    "keyword_name_without_prefix": "Click Element",
                    "keyword_name_with_prefix": "SeleniumLibrary.Click Element",
                    "source": "SeleniumLibrary",
                    "file_usages": 4,
                    "total_usages": 9,
                },
            ]

    app.state.keyword_usage_service = FakeKeywordUsageService()
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_get_most_used_keywords_happy_path_direct(test_app: FastAPI):
    scope: Dict[str, Any] = {"type": "http", "app": test_app}
    request = Request(scope=scope)

    result: MostUsedKeywordsResponse = asyncio.run(
        get_most_used_keywords(request=request)
    )

    assert isinstance(result, MostUsedKeywordsResponse)

    assert len(result.most_used_user_keywords) == 2
    assert len(result.most_used_external_keywords) == 2

    u_first = result.most_used_user_keywords[0]
    assert u_first.keyword_id == "u1"
    assert u_first.file_name == "user1.robot"
    assert u_first.keyword_name_without_prefix == "Login User"
    assert u_first.keyword_name_with_prefix == "Suite.Login User"
    assert u_first.source == "Suite"
    assert u_first.file_usages == 5
    assert u_first.total_usages == 10

    e_first = result.most_used_external_keywords[0]
    assert e_first.keyword_id == "e1"
    assert e_first.file_name == "BuiltIn"
    assert e_first.keyword_name_without_prefix == "Log"
    assert e_first.keyword_name_with_prefix == "BuiltIn.Log"
    assert e_first.source == "BuiltIn"
    assert e_first.file_usages == 8
    assert e_first.total_usages == 15

    service = test_app.state.keyword_usage_service
    assert service.user_called_with_n == 5
    assert service.ext_called_with_n == 5


def test_get_most_used_keywords_happy_path_endpoint(client: TestClient, test_app: FastAPI):
    response = client.get("/most-used-keywords")
    assert response.status_code == 200

    body = response.json()
    parsed = MostUsedKeywordsResponse(**body)

    assert isinstance(parsed, MostUsedKeywordsResponse)

    assert len(parsed.most_used_user_keywords) == 2
    assert len(parsed.most_used_external_keywords) == 2

    u_first = parsed.most_used_user_keywords[0]
    assert u_first.keyword_id == "u1"
    assert u_first.file_name == "user1.robot"
    assert u_first.keyword_name_without_prefix == "Login User"
    assert u_first.keyword_name_with_prefix == "Suite.Login User"
    assert u_first.source == "Suite"
    assert u_first.file_usages == 5
    assert u_first.total_usages == 10

    e_first = parsed.most_used_external_keywords[0]
    assert e_first.keyword_id == "e1"
    assert e_first.file_name == "BuiltIn"
    assert e_first.keyword_name_without_prefix == "Log"
    assert e_first.keyword_name_with_prefix == "BuiltIn.Log"
    assert e_first.source == "BuiltIn"
    assert e_first.file_usages == 8
    assert e_first.total_usages == 15

    service = test_app.state.keyword_usage_service
    assert service.user_called_with_n == 5
    assert service.ext_called_with_n == 5


def test_get_most_used_keywords_empty_result(client: TestClient, test_app: FastAPI, monkeypatch):
    def _empty_user(n: int):
        return []

    def _empty_ext(n: int):
        return []

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_most_used_user_defined_keywords",
        _empty_user,
    )
    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_most_used_external_or_builtin_keywords",
        _empty_ext,
    )

    response = client.get("/most-used-keywords")
    assert response.status_code == 200

    body = response.json()
    parsed = MostUsedKeywordsResponse(**body)
    assert parsed.most_used_user_keywords == []
    assert parsed.most_used_external_keywords == []


def test_get_most_used_keywords_internal_error(client: TestClient, test_app: FastAPI, monkeypatch, caplog):
    def _raise_error(n: int):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_most_used_user_defined_keywords",
        _raise_error,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    response = client.get("/most-used-keywords")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert any(
        "Error fetchin most used keywords" in record.getMessage()
        for record in caplog.records
    )