import logging
from pathlib import Path

from roboview.services.file_register_service import FileRegistryService, logger
from roboview.schemas.domain.common import FileType
from roboview.schemas.domain.files import FileProperties


class FakeDirectoryParser:
    def __init__(self, tests: list[Path] | None = None, resources: list[Path] | None = None):
        self._tests = tests or []
        self._resources = resources or []

    def get_test_file_paths(self) -> list[Path]:
        return self._tests

    def get_resource_file_paths(self) -> list[Path]:
        return self._resources


class FakeModel:
    pass


class FakeLocalKeywordNameFinder:
    def __init__(self) -> None:
        self.keywords: list[str] = []

    def visit(self, model) -> None:  # noqa: D401
        """Fake visit that records having been called."""
        self.keywords = ["Init 1", "Init 2"]


class FakeCalledKeywordFinder:
    def __init__(self) -> None:
        self.called_keywords: list[str] = []

    def visit(self, model) -> None:
        self.called_keywords = ["Call 1", "Call 2"]


class FakeResourceDependencyFinder:
    def __init__(self) -> None:
        self.imports: list[str] = []

    def visit(self, model) -> None:
        self.imports = ["common.resource", "lib.resource"]


def _make_paths(tmp_path: Path) -> tuple[Path, Path]:
    robot = tmp_path / "suite.robot"
    resource = tmp_path / "common.resource"
    robot.touch()
    resource.touch()
    return robot, resource


def test_file_registry_service_initial_state(tmp_path, monkeypatch):
    svc = FileRegistryService(tmp_path)

    monkeypatch.setattr(
        svc,
        "directory_parser",
        FakeDirectoryParser(tests=[], resources=[]),
        raising=True,
    )

    assert svc.get_file_info_list() == []
    assert len(svc.get_file_registry()) == 0


def test_initialize_loads_robot_and_resource_files(tmp_path, monkeypatch):
    robot_file, resource_file = _make_paths(tmp_path)

    svc = FileRegistryService(tmp_path)

    fake_dir = FakeDirectoryParser(tests=[robot_file], resources=[resource_file])
    monkeypatch.setattr(svc, "directory_parser", fake_dir, raising=True)

    def fake_get_model(path: Path):
        assert path == robot_file
        return FakeModel()

    def fake_get_resource_model(path: Path):
        assert path == resource_file
        return FakeModel()

    monkeypatch.setattr(
        "roboview.services.file_register_service.get_model",
        fake_get_model,
        raising=True,
    )
    monkeypatch.setattr(
        "roboview.services.file_register_service.get_resource_model",
        fake_get_resource_model,
        raising=True,
    )

    monkeypatch.setattr(
        "roboview.services.file_register_service.LocalKeywordNameFinder",
        FakeLocalKeywordNameFinder,
        raising=True,
    )
    monkeypatch.setattr(
        "roboview.services.file_register_service.CalledKeywordFinder",
        FakeCalledKeywordFinder,
        raising=True,
    )
    monkeypatch.setattr(
        "roboview.services.file_register_service.ResourceDependencyFinder",
        FakeResourceDependencyFinder,
        raising=True,
    )

    svc.initialize()

    files = svc.get_file_info_list()
    assert len(files) == 2

    by_path = {f.path: f for f in files}
    assert robot_file.as_posix() in by_path
    assert resource_file.as_posix() in by_path

    robot_props = by_path[robot_file.as_posix()]
    res_props = by_path[resource_file.as_posix()]

    assert robot_props.is_resource is False
    assert res_props.is_resource is True

    assert robot_props.initialized_keywords == ["Init 1", "Init 2"]
    assert robot_props.called_keywords == ["Call 1", "Call 2"]
    assert robot_props.imported_files == ["common.resource", "lib.resource"]


def test_initialize_logs_error_if_any_step_fails(tmp_path, monkeypatch, caplog):
    svc = FileRegistryService(tmp_path)

    def broken_load_resources():
        raise RuntimeError("boom")

    monkeypatch.setattr(svc, "_load_resource_files", broken_load_resources, raising=True)

    caplog.set_level(logging.ERROR, logger=logger.name)

    svc.initialize()

    assert any(
        "Failed to initialize file registry" in record.getMessage()
        for record in caplog.records
    )


def test__load_robot_files_handles_directory_parser_error(tmp_path, monkeypatch, caplog):
    svc = FileRegistryService(tmp_path)

    def broken_get_tests():
        raise RuntimeError("boom")

    fake_dir = FakeDirectoryParser()
    monkeypatch.setattr(fake_dir, "get_test_file_paths", broken_get_tests, raising=True)
    monkeypatch.setattr(svc, "directory_parser", fake_dir, raising=True)

    caplog.set_level(logging.ERROR, logger=logger.name)

    svc._load_robot_files()

    assert len(svc.get_file_info_list()) == 0
    assert any(
        "Failed to retrieve file paths from directory parser" in record.getMessage()
        for record in caplog.records
    )


def test__load_resource_files_handles_directory_parser_error(tmp_path, monkeypatch, caplog):
    svc = FileRegistryService(tmp_path)

    def broken_get_resources():
        raise RuntimeError("boom")

    fake_dir = FakeDirectoryParser()
    monkeypatch.setattr(
        fake_dir,
        "get_resource_file_paths",
        broken_get_resources,
        raising=True,
    )
    monkeypatch.setattr(svc, "directory_parser", fake_dir, raising=True)

    caplog.set_level(logging.ERROR, logger=logger.name)

    svc._load_resource_files()

    assert len(svc.get_file_info_list()) == 0
    assert any(
        "Failed to retrieve file paths from directory parser" in record.getMessage()
        for record in caplog.records
    )


def test__load_robot_files_logs_and_continues_on_parse_error(tmp_path, monkeypatch, caplog):
    robot_file, _ = _make_paths(tmp_path)
    svc = FileRegistryService(tmp_path)

    fake_dir = FakeDirectoryParser(tests=[robot_file])
    monkeypatch.setattr(svc, "directory_parser", fake_dir, raising=True)

    def broken_parse_and_register(path: Path, file_type: FileType):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        svc,
        "_parse_and_register_file",
        broken_parse_and_register,
        raising=True,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    svc._load_robot_files()

    assert len(svc.get_file_info_list()) == 0
    assert any(
        f"Failed to process robot file: {robot_file.name}" in record.getMessage()
        for record in caplog.records
    )


def test__load_resource_files_logs_and_continues_on_parse_error(tmp_path, monkeypatch, caplog):
    _, resource_file = _make_paths(tmp_path)
    svc = FileRegistryService(tmp_path)

    fake_dir = FakeDirectoryParser(resources=[resource_file])
    monkeypatch.setattr(svc, "directory_parser", fake_dir, raising=True)

    def broken_parse_and_register(path: Path, file_type: FileType):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        svc,
        "_parse_and_register_file",
        broken_parse_and_register,
        raising=True,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    svc._load_resource_files()

    assert len(svc.get_file_info_list()) == 0
    assert any(
        f"Failed to process resource file: {resource_file.name}" in record.getMessage()
        for record in caplog.records
    )


def test__parse_and_register_file_happy_path(tmp_path, monkeypatch):
    robot_file, _ = _make_paths(tmp_path)
    svc = FileRegistryService(tmp_path)

    monkeypatch.setattr(
        "roboview.services.file_register_service.get_model",
        lambda p: FakeModel(),
        raising=True,
    )
    monkeypatch.setattr(
        "roboview.services.file_register_service.LocalKeywordNameFinder",
        FakeLocalKeywordNameFinder,
        raising=True,
    )
    monkeypatch.setattr(
        "roboview.services.file_register_service.CalledKeywordFinder",
        FakeCalledKeywordFinder,
        raising=True,
    )
    monkeypatch.setattr(
        "roboview.services.file_register_service.ResourceDependencyFinder",
        FakeResourceDependencyFinder,
        raising=True,
    )

    svc._parse_and_register_file(robot_file, FileType.ROBOT)

    files = svc.get_file_info_list()
    assert len(files) == 1
    f = files[0]
    assert isinstance(f, FileProperties)
    assert f.file_name == robot_file.name
    assert f.path == robot_file.as_posix()
    assert f.is_resource is False
    assert f.initialized_keywords == ["Init 1", "Init 2"]
    assert f.called_keywords == ["Call 1", "Call 2"]
    assert f.imported_files == ["common.resource", "lib.resource"]


def test__parse_and_register_file_logs_error_on_exception(tmp_path, monkeypatch, caplog):
    robot_file, _ = _make_paths(tmp_path)
    svc = FileRegistryService(tmp_path)

    def broken_get_model(path: Path):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "roboview.services.file_register_service.get_model",
        broken_get_model,
        raising=True,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    svc._parse_and_register_file(robot_file, FileType.ROBOT)

    assert len(svc.get_file_info_list()) == 0
    assert any(
        f"Error parsing file: {robot_file}" in record.getMessage()
        for record in caplog.records
    )


def test_get_file_registry_returns_internal_registry(tmp_path):
    svc = FileRegistryService(tmp_path)
    reg = svc.get_file_registry()

    assert reg is svc.file_registry