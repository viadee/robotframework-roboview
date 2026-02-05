import asyncio
import logging
from pathlib import Path
from typing import Any, Dict

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from roboview.api.endpoints.system.initialize import (
    router,
    post_initialize_roboview,
    logger,
)
from roboview.schemas.dtos.common import InitializationRequest, InitializationResponse


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/initialize")
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_post_initialize_roboview_happy_path_direct(monkeypatch, test_app: FastAPI, caplog):
    from roboview.api.endpoints.system import initialize as initialize_module

    caplog.set_level(logging.INFO, logger=logger.name)

    class FakeKeywordRegistryService:
        def __init__(self, root: Path) -> None:
            self.root = root
            self.initialized = False

        def initialize(self) -> None:
            self.initialized = True

        def get_keyword_registry(self):
            return {"keywords": ["K1", "K2"]}

    class FakeFileRegistryService:
        def __init__(self, root: Path) -> None:
            self.root = root
            self.initialized = False

        def initialize(self) -> None:
            self.initialized = True

        def get_file_registry(self):
            return {"files": ["f1.robot", "f2.robot"]}

    class FakeRobocopRegistryService:
        def __init__(self, root: Path, config: Path | None) -> None:
            self.root = root
            self.config = config
            self.initialized = False

        def initialize(self) -> None:
            self.initialized = True

        def get_robocop_registry(self):
            return {"messages": ["m1", "m2"]}

    class FakeKeywordUsageService:
        def __init__(self, keyword_registry, file_registry) -> None:
            self.keyword_registry = keyword_registry
            self.file_registry = file_registry

    class FakeKeywordSimilarityService:
        def __init__(self, keyword_registry) -> None:
            self.keyword_registry = keyword_registry
            self.calculated = False

        def calculate_keyword_similarity_matrix(self) -> None:
            self.calculated = True

    class FakeRobocopService:
        def __init__(self, robocop_registry) -> None:
            self.robocop_registry = robocop_registry

    monkeypatch.setattr(
        initialize_module,
        "KeywordRegistryService",
        FakeKeywordRegistryService,
    )
    monkeypatch.setattr(
        initialize_module,
        "FileRegistryService",
        FakeFileRegistryService,
    )
    monkeypatch.setattr(
        initialize_module,
        "RobocopRegistryService",
        FakeRobocopRegistryService,
    )
    monkeypatch.setattr(
        initialize_module,
        "KeywordUsageService",
        FakeKeywordUsageService,
    )
    monkeypatch.setattr(
        initialize_module,
        "KeywordSimilarityService",
        FakeKeywordSimilarityService,
    )
    monkeypatch.setattr(
        initialize_module,
        "RobocopService",
        FakeRobocopService,
    )

    scope: Dict[str, Any] = {"type": "http", "app": test_app}
    request = Request(scope=scope)

    init_req = InitializationRequest(
        project_root_dir="/path/to/project",
        robocop_config_file="/path/to/robocop.toml",
    )

    result: InitializationResponse = asyncio.run(
        post_initialize_roboview(request=request, initialization_request=init_req)
    )

    assert isinstance(result, InitializationResponse)
    assert result.status == "success"

    assert hasattr(test_app.state, "keyword_registry")
    assert hasattr(test_app.state, "file_registry")
    assert hasattr(test_app.state, "robocop_registry")
    assert hasattr(test_app.state, "keyword_usage_service")
    assert hasattr(test_app.state, "keyword_similarity_service")
    assert hasattr(test_app.state, "robocop_service")

    assert any("Initialization Requested" in record.getMessage() for record in caplog.records)
    assert any("Initialize Keyword Usage Service" in record.getMessage() for record in caplog.records)
    assert any("Initialize Keyword Similarity Service" in record.getMessage() for record in caplog.records)
    assert any("Initialize Robocop Service" in record.getMessage() for record in caplog.records)
    assert any("Initialization Successfull" in record.getMessage() for record in caplog.records)


def test_post_initialize_roboview_happy_path_endpoint(monkeypatch, client: TestClient, test_app: FastAPI):
    from roboview.api.endpoints.system import initialize as initialize_module

    class FakeKeywordRegistryService:
        def __init__(self, root: Path) -> None:
            self.root = root

        def initialize(self) -> None:
            pass

        def get_keyword_registry(self):
            return {"keywords": []}

    class FakeFileRegistryService:
        def __init__(self, root: Path) -> None:
            self.root = root

        def initialize(self) -> None:
            pass

        def get_file_registry(self):
            return {"files": []}

    class FakeRobocopRegistryService:
        def __init__(self, root: Path, config: Path | None) -> None:
            self.root = root
            self.config = config

        def initialize(self) -> None:
            pass

        def get_robocop_registry(self):
            return {"messages": []}

    class FakeKeywordUsageService:
        def __init__(self, keyword_registry, file_registry) -> None:
            self.keyword_registry = keyword_registry
            self.file_registry = file_registry

    class FakeKeywordSimilarityService:
        def __init__(self, keyword_registry) -> None:
            self.keyword_registry = keyword_registry

        def calculate_keyword_similarity_matrix(self) -> None:
            pass

    class FakeRobocopService:
        def __init__(self, robocop_registry) -> None:
            self.robocop_registry = robocop_registry

    monkeypatch.setattr(
        initialize_module,
        "KeywordRegistryService",
        FakeKeywordRegistryService,
    )
    monkeypatch.setattr(
        initialize_module,
        "FileRegistryService",
        FakeFileRegistryService,
    )
    monkeypatch.setattr(
        initialize_module,
        "RobocopRegistryService",
        FakeRobocopRegistryService,
    )
    monkeypatch.setattr(
        initialize_module,
        "KeywordUsageService",
        FakeKeywordUsageService,
    )
    monkeypatch.setattr(
        initialize_module,
        "KeywordSimilarityService",
        FakeKeywordSimilarityService,
    )
    monkeypatch.setattr(
        initialize_module,
        "RobocopService",
        FakeRobocopService,
    )

    payload = {
        "project_root_dir": "/path/to/project",
        "robocop_config_file": "/path/to/robocop.toml",
    }

    response = client.post("/initialize", json=payload)
    assert response.status_code == 200

    body = response.json()
    parsed = InitializationResponse(**body)

    assert isinstance(parsed, InitializationResponse)
    assert parsed.status == "success"


def test_post_initialize_roboview_internal_error(monkeypatch, client: TestClient, caplog):
    from roboview.api.endpoints.system import initialize as initialize_module

    def _raise_error(*args, **kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        initialize_module,
        "KeywordRegistryService",
        _raise_error,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    payload = {
        "project_root_dir": "/path/to/project",
        "robocop_config_file": "/path/to/robocop.toml",
    }

    response = client.post("/initialize", json=payload)
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert any(
        "Error initializing Keyword List" in record.getMessage()
        for record in caplog.records
    )