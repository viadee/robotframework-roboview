import asyncio
import logging
from pathlib import Path
from typing import List

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from roboview.api.endpoints.files.robot_files import router, robot_files, logger
from roboview.schemas.domain.files import SelectionFiles
from roboview.schemas.dtos.files import RobotFilesResponse


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/robot-files")
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_robot_files_happy_path(monkeypatch):
    project_root_dir = Path("/path/to/project")

    robot_paths = [
        Path("/path/to/project/tests/robot1.robot"),
        Path("/path/to/project/tests/robot2.robot"),
    ]

    class FakeParser:
        def __init__(self, root: Path) -> None:
            self.root = root

        def get_test_file_paths(self):
            return robot_paths

    created_parsers: list[FakeParser] = []

    def fake_directory_parser_ctor(path: Path) -> FakeParser:
        parser = FakeParser(path)
        created_parsers.append(parser)
        return parser

    monkeypatch.setattr(
        "roboview.api.endpoints.files.robot_files.DirectoryParser",
        fake_directory_parser_ctor,
    )

    result: RobotFilesResponse = asyncio.run(
        robot_files(project_root_dir=project_root_dir)
    )

    assert len(created_parsers) == 1
    assert created_parsers[0].root == project_root_dir

    assert isinstance(result, RobotFilesResponse)
    assert len(result.robot_files) == len(robot_paths)

    expected_robots = [
        SelectionFiles(file_name=p.name, path=p.as_posix())
        for p in robot_paths
    ]

    assert result.robot_files == expected_robots


def test_robot_files_raises_http_500_on_directoryparser_init_error(monkeypatch, caplog):
    project_root_dir = Path("/path/to/project")

    def fake_directory_parser_ctor(_path: Path):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "roboview.api.endpoints.files.robot_files.DirectoryParser",
        fake_directory_parser_ctor,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(robot_files(project_root_dir=project_root_dir))

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"
    assert any(
        "Error fetching resource file names" in record.getMessage()
        for record in caplog.records
    )


def test_robot_files_raises_http_500_when_get_test_file_paths_fails(monkeypatch, caplog):
    project_root_dir = Path("/path/to/project")

    class FakeParser:
        def __init__(self, _root: Path) -> None:
            pass

        def get_test_file_paths(self):
            raise ValueError("broken")

    def fake_directory_parser_ctor(path: Path) -> FakeParser:
        return FakeParser(path)

    monkeypatch.setattr(
        "roboview.api.endpoints.files.robot_files.DirectoryParser",
        fake_directory_parser_ctor,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(robot_files(project_root_dir=project_root_dir))

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"
    assert any(
        "Error fetching resource file names" in record.getMessage()
        for record in caplog.records
    )


def test_get_robot_files_endpoint_happy_path(client: TestClient, monkeypatch):
    project_root_dir = Path("/path/to/project")

    robot_paths = [
        Path("/path/to/project/tests/robot1.robot"),
        Path("/path/to/project/tests/robot2.robot"),
    ]

    class FakeParser:
        def __init__(self, _root: Path) -> None:
            pass

        def get_test_file_paths(self):
            return robot_paths

    def fake_directory_parser_ctor(path: Path) -> FakeParser:
        return FakeParser(path)

    monkeypatch.setattr(
        "roboview.api.endpoints.files.robot_files.DirectoryParser",
        fake_directory_parser_ctor,
    )

    response = client.get(
        "/robot-files",
        params={"project_root_dir": project_root_dir.as_posix()},
    )

    assert response.status_code == 200

    data = response.json()

    expected_robots: List[dict] = [
        {"file_name": p.name, "path": p.as_posix()} for p in robot_paths
    ]

    assert data == {"robot_files": expected_robots}


def test_get_robot_files_endpoint_returns_500_on_error(client: TestClient, monkeypatch):
    project_root_dir = Path("/path/to/project")

    def fake_directory_parser_ctor(_path: Path):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "roboview.api.endpoints.files.robot_files.DirectoryParser",
        fake_directory_parser_ctor,
    )

    response = client.get(
        "/robot-files",
        params={"project_root_dir": project_root_dir.as_posix()},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}