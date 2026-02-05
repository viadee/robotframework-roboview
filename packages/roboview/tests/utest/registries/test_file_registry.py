import logging

from roboview.registries.file_registry import FileRegistry, logger
from roboview.schemas.domain.files import FileProperties


def _make_file(
        file_name: str,
        path: str,
        initialized_keywords: list[str] | None = None,
        called_keywords: list[str] | None = None,
        is_resource: bool = False,
) -> FileProperties:
    return FileProperties(
        file_name=file_name,
        path=path,
        is_resource=is_resource,
        initialized_keywords=initialized_keywords or [],
        called_keywords=called_keywords or [],
    )


def test_initial_state():
    registry = FileRegistry()
    assert len(registry) == 0
    assert registry.get_all_files() == []


def test_register_adds_file_and_len_and_get_all_files_reflect_it():
    registry = FileRegistry()
    f1 = _make_file("file1.robot", "/proj/file1.robot")
    f2 = _make_file("file2.robot", "/proj/file2.robot", is_resource=True)

    registry.register(f1)
    registry.register(f2)

    assert len(registry) == 2
    all_files = registry.get_all_files()
    assert isinstance(all_files, list)
    assert set(f.path for f in all_files) == {"/proj/file1.robot", "/proj/file2.robot"}


def test_register_overwrites_existing_same_name():
    registry = FileRegistry()
    f1 = _make_file("file.robot", "/proj/old.robot")
    f2 = _make_file("file.robot", "/proj/new.robot")

    registry.register(f1)
    registry.register(f2)

    all_files = registry.get_all_files()
    assert len(all_files) == 1
    assert all_files[0].path == "/proj/new.robot"


def test_resolve_returns_matching_file_by_path():
    registry = FileRegistry()
    f1 = _make_file("a.robot", "/proj/a.robot")
    f2 = _make_file("b.robot", "/proj/sub/b.robot", is_resource=True)

    registry.register(f1)
    registry.register(f2)

    assert registry.resolve("/proj/a.robot") is f1
    assert registry.resolve("/proj/sub/b.robot") is f2
    assert registry.resolve("/proj/missing.robot") is None


def test_resolve_handles_empty_path_and_logs_warning(caplog):
    registry = FileRegistry()

    caplog.set_level(logging.WARNING, logger=logger.name)

    result = registry.resolve("")
    assert result is None

    assert any(
        "Empty file path provided to resolve()" in record.getMessage()
        for record in caplog.records
    )


def test_resolve_logs_exception_and_returns_none_on_error(monkeypatch, caplog):
    registry = FileRegistry()
    f = _make_file("x.robot", "/proj/x.robot")
    registry.register(f)

    def broken_get_all():
        raise RuntimeError("boom")

    monkeypatch.setattr(registry, "get_all_files", broken_get_all, raising=True)

    caplog.set_level(logging.ERROR, logger=logger.name)

    result = registry.resolve("/proj/x.robot")
    assert result is None
    assert any(
        "Error while resolving file: /proj/x.robot" in record.getMessage()
        for record in caplog.records
    )


def test_clear_removes_all_files():
    registry = FileRegistry()
    f1 = _make_file("a.robot", "/a")
    f2 = _make_file("b.robot", "/b", is_resource=True)

    registry.register(f1)
    registry.register(f2)
    assert len(registry) == 2

    registry.clear()
    assert len(registry) == 0
    assert registry.get_all_files() == []


def test_contains_uses_resolve_true_case():
    registry = FileRegistry()
    f = _make_file("a.robot", "/a")
    registry.register(f)

    assert "/a" in registry
    assert "/missing" not in registry


def test_register_logs_exception_on_failure(monkeypatch, caplog):
    registry = FileRegistry()
    f = _make_file("a.robot", "/a")

    def broken_setitem(key, value):
        raise RuntimeError("boom")

    class FakeDict(dict):
        def __setitem__(self, key, value):
            broken_setitem(key, value)

    registry._file_registry = FakeDict()  # type: ignore[assignment]

    caplog.set_level(logging.ERROR, logger=logger.name)

    registry.register(f)

    assert len(registry) == 0
    assert any(
        "Failed to register file: /a" in record.getMessage()
        for record in caplog.records
    )