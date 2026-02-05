import asyncio
import logging
from pathlib import Path
from typing import Any, Dict, List

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.requests import Request

from roboview.api.endpoints.overview.kpis import router, get_kpis, logger
from roboview.schemas.dtos.overview import KPIResponse


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/kpis")

    class FakeKeywordUsageService:
        def __init__(self) -> None:
            self.reusage_rate_called = False
            self.doc_coverage_called = False
            self.wo_usages_called = False

        def get_keyword_reusage_rate(self) -> float:
            self.reusage_rate_called = True
            return 0.75

        def get_documentation_coverage(self) -> float:
            self.doc_coverage_called = True
            return 0.6

        def get_keywords_without_usages(self) -> List[dict]:
            self.wo_usages_called = True
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

    class FakeKeywordRegistry:
        def __init__(self) -> None:
            self.get_user_defined_keywords_called = False

        def get_user_defined_keywords(self) -> List[dict]:
            self.get_user_defined_keywords_called = True
            return [
                {"keyword_id": "k1"},
                {"keyword_id": "k2"},
                {"keyword_id": "k3"},
                {"keyword_id": "k4"},
            ]

    class FakeRobocopService:
        def __init__(self) -> None:
            self.get_messages_called = False

        def get_robocop_error_messages(self) -> List[dict]:
            self.get_messages_called = True
            return [
                {"code": "E001", "msg": "Some issue"},
                {"code": "W002", "msg": "Other issue"},
            ]

    app.state.keyword_usage_service = FakeKeywordUsageService()
    app.state.keyword_registry = FakeKeywordRegistry()
    app.state.robocop_service = FakeRobocopService()
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_get_kpis_happy_path_direct(monkeypatch, test_app: FastAPI):
    from roboview.api.endpoints.overview import kpis as kpis_module

    project_root_dir = Path("/path/to/project")

    robot_paths = [
        Path("/path/to/project/tests/test1.robot"),
        Path("/path/to/project/tests/test2.robot"),
    ]
    resource_paths = [
        Path("/path/to/project/resources/res1.resource"),
    ]

    class FakeDirectoryParser:
        def __init__(self, root: Path) -> None:
            self.root = root
            self.get_test_file_paths_called = False
            self.get_resource_file_paths_called = False

        def get_test_file_paths(self):
            self.get_test_file_paths_called = True
            return robot_paths

        def get_resource_file_paths(self):
            self.get_resource_file_paths_called = True
            return resource_paths

    created_parsers: List[FakeDirectoryParser] = []

    def fake_directory_parser_ctor(path: Path) -> FakeDirectoryParser:
        parser = FakeDirectoryParser(path)
        created_parsers.append(parser)
        return parser

    monkeypatch.setattr(
        kpis_module,
        "DirectoryParser",
        fake_directory_parser_ctor,
    )

    scope: Dict[str, Any] = {"type": "http", "app": test_app}
    request = Request(scope=scope)

    result: KPIResponse = asyncio.run(
        get_kpis(request=request, project_root_dir=project_root_dir)
    )

    assert isinstance(result, KPIResponse)

    assert result.keyword_reusage_rate == 0.75
    assert result.documentation_coverage == 0.6
    assert result.num_user_keywords == 4
    assert result.num_unused_keywords == 2
    assert result.num_robocop_issues == 2
    assert result.num_rf_files == len(robot_paths) + len(resource_paths)

    assert len(created_parsers) == 1
    parser = created_parsers[0]
    assert parser.root == project_root_dir
    assert parser.get_test_file_paths_called is True
    assert parser.get_resource_file_paths_called is True

    usage_service = test_app.state.keyword_usage_service
    registry = test_app.state.keyword_registry
    robocop = test_app.state.robocop_service

    assert usage_service.reusage_rate_called is True
    assert usage_service.doc_coverage_called is True
    assert usage_service.wo_usages_called is True
    assert registry.get_user_defined_keywords_called is True
    assert robocop.get_messages_called is True


def test_get_kpis_happy_path_endpoint(monkeypatch, client: TestClient, test_app: FastAPI):
    from roboview.api.endpoints.overview import kpis as kpis_module

    project_root_dir = Path("/path/to/project")

    robot_paths = [
        Path("/path/to/project/tests/test1.robot"),
        Path("/path/to/project/tests/test2.robot"),
        Path("/path/to/project/tests/test3.robot"),
    ]
    resource_paths = [
        Path("/path/to/project/resources/res1.resource"),
        Path("/path/to/project/resources/res2.resource"),
    ]

    class FakeDirectoryParser:
        def __init__(self, root: Path) -> None:
            self.root = root

        def get_test_file_paths(self):
            return robot_paths

        def get_resource_file_paths(self):
            return resource_paths

    def fake_directory_parser_ctor(path: Path) -> FakeDirectoryParser:
        return FakeDirectoryParser(path)

    monkeypatch.setattr(
        kpis_module,
        "DirectoryParser",
        fake_directory_parser_ctor,
    )

    response = client.get(
        "/kpis",
        params={"project_root_dir": project_root_dir.as_posix()},
    )
    assert response.status_code == 200

    body = response.json()
    parsed = KPIResponse(**body)

    assert parsed.keyword_reusage_rate == 0.75
    assert parsed.documentation_coverage == 0.6
    assert parsed.num_user_keywords == 4
    assert parsed.num_unused_keywords == 2
    assert parsed.num_robocop_issues == 2
    assert parsed.num_rf_files == len(robot_paths) + len(resource_paths)


def test_get_kpis_internal_error_on_directory_parser(monkeypatch, client: TestClient):
    from roboview.api.endpoints.overview import kpis as kpis_module

    def fake_directory_parser_ctor(path: Path):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        kpis_module,
        "DirectoryParser",
        fake_directory_parser_ctor,
    )

    response = client.get(
        "/kpis",
        params={"project_root_dir": "/path/to/project"},
    )
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}


def test_get_kpis_internal_error_on_services(monkeypatch, client: TestClient, test_app: FastAPI, caplog):
    def _raise_error():
        raise RuntimeError("boom")

    monkeypatch.setattr(
        test_app.state.keyword_usage_service,
        "get_keyword_reusage_rate",
        _raise_error,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    response = client.get(
        "/kpis",
        params={"project_root_dir": "/path/to/project"},
    )
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}
    assert any(
        "Error calculating KPIs" in record.getMessage()
        for record in caplog.records
    )