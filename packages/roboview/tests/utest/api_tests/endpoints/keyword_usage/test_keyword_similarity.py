import asyncio
import logging
from typing import Any, Dict

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from roboview.api.endpoints.keyword_usage.keyword_similarity import (
    router,
    get_keyword_similarity,
    logger,
)
from roboview.schemas.dtos.keyword_similarity import KeywordSimilarityResponse


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/keyword-similarity")

    class FakeKeywordSimilarityService:
        def __init__(self) -> None:
            self.called_with_keyword_name = None
            self.called_with_top_n = None

        def get_n_most_similar_keywords(self, keyword_name: str, top_n: int):
            self.called_with_keyword_name = keyword_name
            self.called_with_top_n = top_n
            return [
                {
                    "keyword_id": "k1",
                    "keyword_name_without_prefix": "Login User",
                    "keyword_name_with_prefix": "MyLib.Login User",
                    "source": "MyLib",
                    "score": 0.95,
                },
                {
                    "keyword_id": "k2",
                    "keyword_name_without_prefix": "User Login",
                    "keyword_name_with_prefix": "MyLib.User Login",
                    "source": "MyLib",
                    "score": 0.92,
                },
                {
                    "keyword_id": "k3",
                    "keyword_name_without_prefix": "Login",
                    "keyword_name_with_prefix": "MyLib.Login",
                    "source": "MyLib",
                    "score": 0.90,
                },
                {
                    "keyword_id": "k4",
                    "keyword_name_without_prefix": "Authenticate User",
                    "keyword_name_with_prefix": "MyLib.Authenticate User",
                    "source": "MyLib",
                    "score": 0.88,
                },
                {
                    "keyword_id": "k5",
                    "keyword_name_without_prefix": "Sign In",
                    "keyword_name_with_prefix": "MyLib.Sign In",
                    "source": "MyLib",
                    "score": 0.87,
                },
            ]

    app.state.keyword_similarity_service = FakeKeywordSimilarityService()
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_get_keyword_similarity_happy_path_direct(test_app: FastAPI):
    scope: Dict[str, Any] = {"type": "http", "app": test_app}
    request = Request(scope=scope)

    result: KeywordSimilarityResponse = asyncio.run(
        get_keyword_similarity(request=request, keyword_name="Login User")
    )

    assert isinstance(result, KeywordSimilarityResponse)
    assert len(result.top_n_similar_keywords) == 5

    first = result.top_n_similar_keywords[0]
    assert first.keyword_id == "k1"
    assert first.keyword_name_without_prefix == "Login User"
    assert first.keyword_name_with_prefix == "MyLib.Login User"
    assert first.source == "MyLib"
    assert first.score == 0.95

    service = test_app.state.keyword_similarity_service
    assert service.called_with_keyword_name == "Login User"
    assert service.called_with_top_n == 5


def test_get_keyword_similarity_happy_path(client: TestClient, test_app: FastAPI):
    response = client.get("/keyword-similarity", params={"keyword_name": "Login User"})
    assert response.status_code == 200

    body = response.json()
    parsed = KeywordSimilarityResponse(**body)

    assert isinstance(parsed, KeywordSimilarityResponse)
    assert len(parsed.top_n_similar_keywords) == 5

    first = parsed.top_n_similar_keywords[0]
    assert first.keyword_id == "k1"
    assert first.keyword_name_without_prefix == "Login User"
    assert first.keyword_name_with_prefix == "MyLib.Login User"
    assert first.source == "MyLib"
    assert first.score == 0.95

    service = test_app.state.keyword_similarity_service
    assert service.called_with_keyword_name == "Login User"
    assert service.called_with_top_n == 5


def test_get_keyword_similarity_empty_result(client: TestClient, test_app: FastAPI, monkeypatch):
    def _empty_return(keyword_name: str, top_n: int):
        return []

    monkeypatch.setattr(
        test_app.state.keyword_similarity_service,
        "get_n_most_similar_keywords",
        _empty_return,
    )

    response = client.get("/keyword-similarity", params={"keyword_name": "Login User"})
    assert response.status_code == 200

    body = response.json()
    parsed = KeywordSimilarityResponse(**body)
    assert parsed.top_n_similar_keywords == []


def test_get_keyword_similarity_internal_error(client: TestClient, test_app: FastAPI, monkeypatch, caplog):
    def _raise_error(keyword_name: str, top_n: int):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        test_app.state.keyword_similarity_service,
        "get_n_most_similar_keywords",
        _raise_error,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    response = client.get("/keyword-similarity", params={"keyword_name": "Login User"})
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert any(
        "Error retrieving similarity values for keyword Login User" in record.getMessage()
        for record in caplog.records
    )