import logging
from pathlib import Path

from roboview.services.keyword_register_service import (
    KeywordRegistryService,
    logger,
)
from roboview.schemas.domain.common import FileType, LibraryType
from roboview.schemas.domain.keywords import KeywordProperties


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


class FakeLocalKeywordFinder:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path
        self.keyword_doc: list[KeywordProperties] = []

    def visit(self, model) -> None:
        self.keyword_doc = [
            KeywordProperties(
                file_name=self.file_path.name,
                keyword_name_without_prefix="KW One",
                keyword_name_with_prefix=f"{self.file_path.stem}.KW One",
                description="First kw",
                is_user_defined=True,
                code="KW One",
                source=self.file_path.as_posix(),
                validation_str_without_prefix="kwone",
                validation_str_with_prefix=f"{self.file_path.stem}.kwone",
            ),
            KeywordProperties(
                file_name=self.file_path.name,
                keyword_name_without_prefix="KW Two",
                keyword_name_with_prefix=f"{self.file_path.stem}.KW Two",
                description="Second kw",
                is_user_defined=True,
                code="KW Two",
                source=self.file_path.as_posix(),
                validation_str_without_prefix="kwtwo",
                validation_str_with_prefix=f"{self.file_path.stem}.kwtwo",
            ),
        ]


class FakeKeywordDependencyFinder:
    def __init__(self, file_path: Path) -> None:
        self.file_path = file_path

    def visit(self, model) -> None:
        pass

    def get_formatted_result(self) -> list[dict]:
        return [
            {
                "keyword_name": "KW One",
                "called_keywords": ["Lib KW", "KW Two"],
            },
            {
                "keyword_name": "KW Two",
                "called_keywords": [],
            },
        ]


class FakeLibraryKeyword:
    def __init__(self, name: str, doc: str):
        self.name = name
        self.doc = doc


class FakeLibraryDocumentation:
    def __init__(self, lib_name: str) -> None:
        self.name = lib_name
        self.keywords = [
            FakeLibraryKeyword("Open Browser", "Open a new browser"),
            FakeLibraryKeyword("Click", "Click element"),
        ]


def _make_paths(tmp_path: Path) -> tuple[Path, Path]:
    robot = tmp_path / "suite.robot"
    resource = tmp_path / "common.resource"
    robot.touch()
    resource.touch()
    return robot, resource


def test_keyword_registry_service_initial_state(tmp_path, monkeypatch):
    svc = KeywordRegistryService(tmp_path)

    monkeypatch.setattr(
        svc,
        "directory_parser",
        FakeDirectoryParser(tests=[], resources=[]),
        raising=True,
    )

    assert svc.get_keyword_info_list() == []
    assert len(svc.get_keyword_registry()) == 0


def test_initialize_loads_local_and_library_keywords(tmp_path, monkeypatch):
    robot_file, resource_file = _make_paths(tmp_path)
    svc = KeywordRegistryService(tmp_path)

    fake_dir = FakeDirectoryParser(tests=[robot_file], resources=[resource_file])
    monkeypatch.setattr(svc, "directory_parser", fake_dir, raising=True)

    monkeypatch.setattr(
        "roboview.services.keyword_register_service.get_model",
        lambda p: FakeModel(),
        raising=True,
    )
    monkeypatch.setattr(
        "roboview.services.keyword_register_service.get_resource_model",
        lambda p: FakeModel(),
        raising=True,
    )

    monkeypatch.setattr(
        "roboview.services.keyword_register_service.LocalKeywordFinder",
        FakeLocalKeywordFinder,
        raising=True,
    )
    monkeypatch.setattr(
        "roboview.services.keyword_register_service.KeywordDependencyFinder",
        FakeKeywordDependencyFinder,
        raising=True,
    )

    def fake_get_library_keywords(library_type: LibraryType) -> list[KeywordProperties]:
        base = library_type.value
        return [
            KeywordProperties(
                file_name=base,
                keyword_name_without_prefix=f"{base} KW1",
                keyword_name_with_prefix=f"{base}.{base} KW1",
                description="Lib kw1",
                is_user_defined=False,
                code="",
                source=base,
                validation_str_without_prefix=f"{base}kw1".lower().replace(" ", "").replace("_", ""),
                validation_str_with_prefix=f"{base}.{base}kw1".lower().replace(" ", "").replace("_", ""),
            ),
            KeywordProperties(
                file_name=base,
                keyword_name_without_prefix=f"{base} KW2",
                keyword_name_with_prefix=f"{base}.{base} KW2",
                description="Lib kw2",
                is_user_defined=False,
                code="",
                source=base,
                validation_str_without_prefix=f"{base}kw2".lower().replace(" ", "").replace("_", ""),
                validation_str_with_prefix=f"{base}.{base}kw2".lower().replace(" ", "").replace("_", ""),
            ),
        ]

    monkeypatch.setattr(
        "roboview.services.keyword_register_service.KeywordRegistryService._get_library_keywords",
        staticmethod(fake_get_library_keywords),  # type: ignore[arg-type]
        raising=False,
    )

    svc.initialize()

    all_keywords = svc.get_keyword_info_list()
    assert len(all_keywords) == 12

    local = [
        k
        for k in all_keywords
        if k.is_user_defined and k.file_name in {robot_file.name, resource_file.name}
    ]
    assert len(local) == 4
    names_to_calls = {k.keyword_name_without_prefix: (k.called_keywords or []) for k in local}
    assert "KW One" in names_to_calls
    assert "KW Two" in names_to_calls
    assert names_to_calls["KW One"] == ["Lib KW", "KW Two"]
    assert names_to_calls["KW Two"] == []


def test_initialize_logs_error_if_any_step_fails(tmp_path, monkeypatch, caplog):
    svc = KeywordRegistryService(tmp_path)

    def broken_load_local():
        raise RuntimeError("boom")

    monkeypatch.setattr(svc, "_load_local_keywords", broken_load_local, raising=True)

    caplog.set_level(logging.ERROR, logger=logger.name)

    svc.initialize()

    assert any(
        "Failed to initialize keyword registry" in record.getMessage()
        for record in caplog.records
    )


def test__load_local_keywords_handles_directory_parser_error(tmp_path, monkeypatch, caplog):
    svc = KeywordRegistryService(tmp_path)

    def broken_get_tests():
        raise RuntimeError("boom")

    fake_dir = FakeDirectoryParser()
    monkeypatch.setattr(fake_dir, "get_test_file_paths", broken_get_tests, raising=True)
    monkeypatch.setattr(svc, "directory_parser", fake_dir, raising=True)

    caplog.set_level(logging.ERROR, logger=logger.name)

    svc._load_local_keywords()

    assert len(svc.get_keyword_info_list()) == 0
    assert any(
        "Failed to retrieve file paths from directory parser" in record.getMessage()
        for record in caplog.records
    )


def test__load_local_keywords_logs_and_continues_on_parse_error(tmp_path, monkeypatch, caplog):
    robot_file, resource_file = _make_paths(tmp_path)
    svc = KeywordRegistryService(tmp_path)

    fake_dir = FakeDirectoryParser(tests=[robot_file], resources=[resource_file])
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

    svc._load_local_keywords()

    assert len(svc.get_keyword_info_list()) == 0
    assert any(
        f"Failed to process resource file: {resource_file.name}" in record.getMessage()
        for record in caplog.records
    )
    assert any(
        f"Failed to process robot file: {robot_file.name}" in record.getMessage()
        for record in caplog.records
    )


def test__parse_and_register_file_happy_path(tmp_path, monkeypatch):
    robot_file, _ = _make_paths(tmp_path)
    svc = KeywordRegistryService(tmp_path)

    monkeypatch.setattr(
        "roboview.services.keyword_register_service.get_model",
        lambda p: FakeModel(),
        raising=True,
    )
    monkeypatch.setattr(
        "roboview.services.keyword_register_service.get_resource_model",
        lambda p: FakeModel(),
        raising=True,
    )
    monkeypatch.setattr(
        "roboview.services.keyword_register_service.LocalKeywordFinder",
        FakeLocalKeywordFinder,
        raising=True,
    )
    monkeypatch.setattr(
        "roboview.services.keyword_register_service.KeywordDependencyFinder",
        FakeKeywordDependencyFinder,
        raising=True,
    )

    svc._parse_and_register_file(robot_file, FileType.ROBOT)

    kws = svc.get_keyword_info_list()
    assert len(kws) == 2

    by_name = {k.keyword_name_without_prefix: k for k in kws}
    assert "KW One" in by_name
    assert "KW Two" in by_name

    assert by_name["KW One"].called_keywords == ["Lib KW", "KW Two"]
    assert by_name["KW Two"].called_keywords == []


def test__enrich_with_called_keywords_uses_dependency_map(monkeypatch):
    dummy_path = Path("/proj/file.robot")
    finder = FakeKeywordDependencyFinder(dummy_path)

    kw_props = KeywordProperties(
        file_name="file.robot",
        keyword_name_without_prefix="KW One",
        keyword_name_with_prefix="file.KW One",
        description=None,
        is_user_defined=True,
        code="",
        source="/proj/file.robot",
        validation_str_without_prefix="kwone",
        validation_str_with_prefix="file.kwone",
    )

    enriched = KeywordRegistryService._enrich_with_called_keywords(finder, kw_props)

    assert enriched.called_keywords == ["Lib KW", "KW Two"]


def test__enrich_with_called_keywords_defaults_to_empty_list_for_missing_key():
    dummy_path = Path("/proj/file.robot")
    finder = FakeKeywordDependencyFinder(dummy_path)

    kw_props = KeywordProperties(
        file_name="file.robot",
        keyword_name_without_prefix="Unknown KW",
        keyword_name_with_prefix="file.Unknown KW",
        description=None,
        is_user_defined=True,
        code="",
        source="/proj/file.robot",
        validation_str_without_prefix="unknownkw",
        validation_str_with_prefix="file.unknownkw",
    )

    enriched = KeywordRegistryService._enrich_with_called_keywords(finder, kw_props)

    assert enriched.called_keywords == []


def test__load_library_keywords_registers_keywords_and_logs_on_failure(tmp_path, monkeypatch, caplog):
    svc = KeywordRegistryService(tmp_path)

    def fake_get_library_keywords(library_type: LibraryType) -> list[KeywordProperties]:
        if library_type is LibraryType.BROWSER:
            return [
                KeywordProperties(
                    file_name="Browser",
                    keyword_name_without_prefix="Open Browser",
                    keyword_name_with_prefix="Browser.Open Browser",
                    description="Open browser",
                    is_user_defined=False,
                    code="",
                    source="Browser",
                    validation_str_without_prefix="openbrowser",
                    validation_str_with_prefix="browser.openbrowser",
                )
            ]
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "roboview.services.keyword_register_service.KeywordRegistryService._get_library_keywords",
        staticmethod(fake_get_library_keywords),  # type: ignore[arg-type]
        raising=False,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    svc._load_library_keywords()

    all_kws = svc.get_keyword_info_list()
    assert len(all_kws) == 1
    assert all_kws[0].keyword_name_without_prefix == "Open Browser"

    for lib in (LibraryType.SELENIUM, LibraryType.DATABASE, LibraryType.BUILTIN):
        assert any(
            f"Failed to load library: {lib.value}" in record.getMessage()
            for record in caplog.records
        )


def test__get_library_keywords_happy_path(monkeypatch):
    lib_name = "Browser"

    def fake_libdoc(name: str):
        assert name == lib_name
        return FakeLibraryDocumentation(name)

    monkeypatch.setattr(
        "roboview.services.keyword_register_service.LibraryDocumentation",
        fake_libdoc,
        raising=True,
    )

    kws = KeywordRegistryService._get_library_keywords(LibraryType.BROWSER)

    assert len(kws) == 2
    names = {k.keyword_name_without_prefix for k in kws}
    assert names == {"Open Browser", "Click"}
    for k in kws:
        assert k.is_user_defined is False
        assert k.file_name == lib_name
        assert k.source == lib_name
        assert k.keyword_name_with_prefix.startswith(f"{lib_name}.")


def test__get_library_keywords_returns_empty_list_on_exception(monkeypatch, caplog):
    def broken_libdoc(name: str):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "roboview.services.keyword_register_service.LibraryDocumentation",
        broken_libdoc,
        raising=True,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    kws = KeywordRegistryService._get_library_keywords(LibraryType.BROWSER)

    assert kws == []
    assert any(
        "Library Browser could not be loaded" in record.getMessage()
        for record in caplog.records
    )


def test_get_keyword_registry_returns_internal_registry(tmp_path):
    svc = KeywordRegistryService(tmp_path)
    reg = svc.get_keyword_registry()

    assert reg is svc.registry