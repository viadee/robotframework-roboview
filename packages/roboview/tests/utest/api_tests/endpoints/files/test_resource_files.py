import asyncio
import logging
from pathlib import Path
from typing import List

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from roboview.api.endpoints.files.resource_files import router, resource_files, logger
from roboview.schemas.domain.files import SelectionFiles
from roboview.schemas.dtos.files import ResourceFilesResponse


@pytest.fixture
def test_app() -> FastAPI:
    app = FastAPI()
    app.include_router(router, prefix="/resource-files")
    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    return TestClient(test_app)


def test_resource_files_happy_path(monkeypatch):
    project_root_dir = Path("/path/to/project")

    resource_paths = [
        Path("/path/to/project/resources/res1.resource"),
        Path("/path/to/project/resources/res2.resource"),
    ]

    class FakeParser:
        def __init__(self, root: Path) -> None:
            self.root = root

        def get_resource_file_paths(self):
            return resource_paths

    created_parsers: list[FakeParser] = []

    def fake_directory_parser_ctor(path: Path) -> FakeParser:
        parser = FakeParser(path)
        created_parsers.append(parser)
        return parser

    monkeypatch.setattr(
        "roboview.api.endpoints.files.resource_files.DirectoryParser",
        fake_directory_parser_ctor,
    )

    result: ResourceFilesResponse = asyncio.run(
        resource_files(project_root_dir=project_root_dir)
    )

    assert len(created_parsers) == 1
    assert created_parsers[0].root == project_root_dir

    assert isinstance(result, ResourceFilesResponse)
    assert len(result.resource_files) == len(resource_paths)

    expected_resources = [
        SelectionFiles(file_name=p.name, path=p.as_posix())
        for p in resource_paths
    ]

    assert result.resource_files == expected_resources


def test_resource_files_raises_http_500_on_directoryparser_init_error(monkeypatch, caplog):
    project_root_dir = Path("/path/to/project")

    def fake_directory_parser_ctor(_path: Path):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "roboview.api.endpoints.files.resource_files.DirectoryParser",
        fake_directory_parser_ctor,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(resource_files(project_root_dir=project_root_dir))

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"
    assert any(
        "Error fetching resource file names" in record.getMessage()
        for record in caplog.records
    )


def test_resource_files_raises_http_500_when_get_resource_file_paths_fails(monkeypatch, caplog):
    project_root_dir = Path("/path/to/project")

    class FakeParser:
        def __init__(self, _root: Path) -> None:
            pass

        def get_resource_file_paths(self):
            raise ValueError("broken")

    def fake_directory_parser_ctor(path: Path) -> FakeParser:
        return FakeParser(path)

    monkeypatch.setattr(
        "roboview.api.endpoints.files.resource_files.DirectoryParser",
        fake_directory_parser_ctor,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(resource_files(project_root_dir=project_root_dir))

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal Server Error"
    assert any(
        "Error fetching resource file names" in record.getMessage()
        for record in caplog.records
    )


def test_get_resource_files_endpoint_happy_path(client: TestClient, monkeypatch):
    project_root_dir = Path("/path/to/project")

    resource_paths = [
        Path("/path/to/project/resources/res1.resource"),
        Path("/path/to/project/resources/res2.resource"),
    ]

    class FakeParser:
        def __init__(self, _root: Path) -> None:
            pass

        def get_resource_file_paths(self):
            return resource_paths

    def fake_directory_parser_ctor(path: Path) -> FakeParser:
        return FakeParser(path)

    monkeypatch.setattr(
        "roboview.api.endpoints.files.resource_files.DirectoryParser",
        fake_directory_parser_ctor,
    )

    response = client.get(
        "/resource-files",
        params={"project_root_dir": project_root_dir.as_posix()},
    )

    assert response.status_code == 200

    data = response.json()

    expected_resources: List[dict] = [
        {"file_name": p.name, "path": p.as_posix()} for p in resource_paths
    ]

    assert data == {"resource_files": expected_resources}


def test_get_resource_files_endpoint_returns_500_on_error(client: TestClient, monkeypatch):
    project_root_dir = Path("/path/to/project")

    def fake_directory_parser_ctor(_path: Path):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "roboview.api.endpoints.files.resource_files.DirectoryParser",
        fake_directory_parser_ctor,
    )

    response = client.get(
        "/resource-files",
        params={"project_root_dir": project_root_dir.as_posix()},
    )

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal Server Error"}