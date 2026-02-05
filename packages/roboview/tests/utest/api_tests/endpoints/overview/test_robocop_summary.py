import asyncio
import logging
from typing import Any, Dict, List

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from roboview.api.endpoints.overview.robocop_summary import (
    router,
    get_robocop_issue_summary,
    logger,
)
from roboview.schemas.dtos.overview import RobocopIssueSummaryResponse


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/robocop-summary")

    class FakeRobocopService:
        def __init__(self) -> None:
            self.called = False

        def get_robocop_issue_summary(self) -> List[dict]:
            self.called = True
            return [
                {"category": "ERROR", "count": 3},
                {"category": "WARNING", "count": 5},
                {"category": "INFO", "count": 2},
            ]

    app.state.robocop_service = FakeRobocopService()
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_get_robocop_issue_summary_happy_path_direct(test_app: FastAPI):
    scope: Dict[str, Any] = {"type": "http", "app": test_app}
    request = Request(scope=scope)

    result: RobocopIssueSummaryResponse = asyncio.run(
        get_robocop_issue_summary(request=request)
    )

    assert isinstance(result, RobocopIssueSummaryResponse)
    assert len(result.robocop_issue_summary) == 3

    first = result.robocop_issue_summary[0]
    assert first.category == "ERROR"
    assert first.count == 3

    service = test_app.state.robocop_service
    assert service.called is True


def test_get_robocop_issue_summary_happy_path_endpoint(client: TestClient, test_app: FastAPI):
    response = client.get("/robocop-summary")
    assert response.status_code == 200

    body = response.json()
    parsed = RobocopIssueSummaryResponse(**body)

    assert isinstance(parsed, RobocopIssueSummaryResponse)
    assert len(parsed.robocop_issue_summary) == 3

    first = parsed.robocop_issue_summary[0]
    assert first.category == "ERROR"
    assert first.count == 3

    service = test_app.state.robocop_service
    assert service.called is True


def test_get_robocop_issue_summary_empty_result(client: TestClient, test_app: FastAPI, monkeypatch):
    def _empty_return():
        return []

    monkeypatch.setattr(
        test_app.state.robocop_service,
        "get_robocop_issue_summary",
        _empty_return,
    )

    response = client.get("/robocop-summary")
    assert response.status_code == 200

    body = response.json()
    parsed = RobocopIssueSummaryResponse(**body)
    assert parsed.robocop_issue_summary == []


def test_get_robocop_issue_summary_internal_error(client: TestClient, test_app: FastAPI, monkeypatch, caplog):
    def _raise_error():
        raise RuntimeError("boom")

    monkeypatch.setattr(
        test_app.state.robocop_service,
        "get_robocop_issue_summary",
        _raise_error,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    response = client.get("/robocop-summary")
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert any(
        "Error calculating KPIs" in record.getMessage()
        for record in caplog.records
    )