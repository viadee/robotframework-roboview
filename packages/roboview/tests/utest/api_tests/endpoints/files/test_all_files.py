import asyncio
import logging
from pathlib import Path
from typing import List

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from roboview.api.endpoints.files.all_files import router, all_files, logger
from roboview.schemas.domain.files import SelectionFiles
from roboview.schemas.dtos.files import AllFilesResponse


@pytest.fixture
def test_app() -> FastAPI:
    """Create a small FastAPI app including only the all_files router."""
    app = FastAPI()
    app.include_router(router, prefix="/all-files")
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_all_files_happy_path(monkeypatch):
    project_root_dir = "/path/to/project"

    robot_paths = [
        Path("/path/to/project/tests/robot1.robot"),
        Path("/path/to/project/tests/robot2.robot"),
    ]
    resource_paths = [
        Path("/path/to/project/resources/res1.resource"),
    ]

    class FakeParser:
        def __init__(self, root: Path) -> None:
            self.root = root

        def get_test_file_paths(self):
            return robot_paths

        def get_resource_file_paths(self):
            return resource_paths

    created_parsers: list[FakeParser] = []

    def fake_directory_parser_ctor(path: Path) -> FakeParser:
        parser = FakeParser(path)
        created_parsers.append(parser)
        return parser

    monkeypatch.setattr(
        "roboview.api.endpoints.files.all_files.DirectoryParser",
        fake_directory_parser_ctor,
    )

    result: AllFilesResponse = asyncio.run(
        all_files(project_root_dir=project_root_dir)
    )

    assert len(created_parsers) == 1
    assert created_parsers[0].root == Path(project_root_dir)

    assert isinstance(result, AllFilesResponse)
    assert len(result.all_files) == len(robot_paths) + len(resource_paths)

    expected_robot = [
        SelectionFiles(file_name=p.name, path=p.as_posix()) for p in robot_paths
    ]
    expected_resources = [
        SelectionFiles(file_name=p.name, path=p.as_posix()) for p in resource_paths
    ]

    assert result.all_files == expected_robot + expected_resources


def test_all_files_raises_http_500_on_directoryparser_init_error(monkeypatch, caplog):
    project_root_dir = "/path/to/project"

    def fake_directory_parser_ctor(_path: Path):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "roboview.api.endpoints.files.all_files.DirectoryParser",
        fake_directory_parser_ctor,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(all_files(project_root_dir=project_root_dir))

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"
    assert any(
        "Error fetching Robot Framework files" in record.getMessage()
        for record in caplog.records
    )


def test_all_files_raises_http_500_when_get_test_file_paths_fails(monkeypatch, caplog):
    project_root_dir = "/path/to/project"

    class FakeParser:
        def __init__(self, _root: Path) -> None:
            pass

        def get_test_file_paths(self):
            raise ValueError("broken")

        def get_resource_file_paths(self):
            return []

    def fake_directory_parser_ctor(path: Path) -> FakeParser:
        return FakeParser(path)

    monkeypatch.setattr(
        "roboview.api.endpoints.files.all_files.DirectoryParser",
        fake_directory_parser_ctor,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(all_files(project_root_dir=project_root_dir))

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"
    assert any(
        "Error fetching Robot Framework files" in record.getMessage()
        for record in caplog.records
    )


def test_get_all_files_endpoint_happy_path(client: TestClient, monkeypatch):
    project_root_dir = "/path/to/project"

    robot_paths = [
        Path("/path/to/project/tests/robot1.robot"),
    ]
    resource_paths = [
        Path("/path/to/project/resources/res1.resource"),
        Path("/path/to/project/resources/res2.resource"),
    ]

    class FakeParser:
        def __init__(self, _root: Path) -> None:
            pass

        def get_test_file_paths(self):
            return robot_paths

        def get_resource_file_paths(self):
            return resource_paths

    def fake_directory_parser_ctor(path: Path) -> FakeParser:
        return FakeParser(path)

    monkeypatch.setattr(
        "roboview.api.endpoints.files.all_files.DirectoryParser",
        fake_directory_parser_ctor,
    )

    response = client.get("/all-files", params={"project_root_dir": project_root_dir})

    assert response.status_code == 200

    data = response.json()

    expected_robot = [
        {"file_name": p.name, "path": p.as_posix()} for p in robot_paths
    ]
    expected_resources = [
        {"file_name": p.name, "path": p.as_posix()} for p in resource_paths
    ]
    expected_all_files: List[dict] = expected_robot + expected_resources

    assert data == {"all_files": expected_all_files}


def test_get_all_files_endpoint_returns_500_on_error(client: TestClient, monkeypatch):
    project_root_dir = "/path/to/project"

    def fake_directory_parser_ctor(_path: Path):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "roboview.api.endpoints.files.all_files.DirectoryParser",
        fake_directory_parser_ctor,
    )

    response = client.get("/all-files", params={"project_root_dir": project_root_dir})

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}