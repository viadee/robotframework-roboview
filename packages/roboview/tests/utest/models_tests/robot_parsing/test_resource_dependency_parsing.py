import logging

from roboview.models.robot_parsing.resource_dependency_parsing import (
    ResourceDependencyFinder,
    logger,
)


class FakeResourceSetting:
    def __init__(self, import_value):
        self.type = "RESOURCE"
        self._import_value = import_value

    def get_value(self, token_type):
        return self._import_value


class FakeOtherSetting:
    def __init__(self):
        self.type = "LIBRARY"

    def get_value(self, token_type):
        return "ShouldNotMatter"


class FakeSettingSection:
    def __init__(self, body):
        self.body = body


def test_initial_state():
    finder = ResourceDependencyFinder()
    assert finder.imports == []


def test_collects_simple_resource_imports():
    finder = ResourceDependencyFinder()

    section = FakeSettingSection(
        [
            FakeResourceSetting("common.resource"),
            FakeResourceSetting("sub/other.resource"),
        ]
    )

    finder.visit_SettingSection(section)  # type: ignore[arg-type]

    assert finder.imports == ["common.resource", "other.resource"]


def test_ignores_non_resource_settings():
    finder = ResourceDependencyFinder()

    section = FakeSettingSection(
        [
            FakeOtherSetting(),
            FakeResourceSetting("a/b/c.resource"),
        ]
    )

    finder.visit_SettingSection(section)  # type: ignore[arg-type]

    assert finder.imports == ["c.resource"]


def test_normalizes_variable_separators():
    finder = ResourceDependencyFinder()

    section = FakeSettingSection(
        [
            FakeResourceSetting("${/}path${/}to${/}file.resource"),
            FakeResourceSetting("{/}another{/}dir{/}lib.resource"),
        ]
    )

    finder.visit_SettingSection(section)  # type: ignore[arg-type]

    assert finder.imports == ["file.resource", "lib.resource"]


def test_logs_when_import_value_is_none(caplog):
    class NoneValueSetting:
        def __init__(self):
            self.type = "RESOURCE"

        def get_value(self, token_type):
            return None

    finder = ResourceDependencyFinder()

    section = FakeSettingSection([NoneValueSetting()])

    caplog.set_level(logging.ERROR, logger=logger.name)

    finder.visit_SettingSection(section)  # type: ignore[arg-type]

    assert finder.imports == []
    assert any(
        "Import value is None." in record.getMessage()
        for record in caplog.records
    )


def test_logs_when_import_value_is_not_string(caplog):
    class NonStrSetting:
        def __init__(self):
            self.type = "RESOURCE"

        def get_value(self, token_type):
            return 123

    finder = ResourceDependencyFinder()

    section = FakeSettingSection([NonStrSetting()])

    caplog.set_level(logging.ERROR, logger=logger.name)

    finder.visit_SettingSection(section)  # type: ignore[arg-type]

    assert finder.imports == []
    assert any(
        "Expected a string but got unknown." in record.getMessage()
        for record in caplog.records
    )


def test_logs_attribute_error(caplog):
    class MissingTypeSetting:
        def get_value(self, token_type):
            return "something.resource"

    finder = ResourceDependencyFinder()

    section = FakeSettingSection([MissingTypeSetting()])

    caplog.set_level(logging.ERROR, logger=logger.name)

    finder.visit_SettingSection(section)  # type: ignore[arg-type]

    assert finder.imports == []
    assert any(
        "Setting item missing, expected attributes" in record.getMessage()
        for record in caplog.records
    )


def test_logs_unexpected_error(caplog, monkeypatch):
    class BrokenSetting(FakeResourceSetting):
        def get_value(self, token_type):
            raise RuntimeError("boom")

    finder = ResourceDependencyFinder()
    section = FakeSettingSection([BrokenSetting("x.resource")])

    caplog.set_level(logging.ERROR, logger=logger.name)

    finder.visit_SettingSection(section)  # type: ignore[arg-type]

    assert finder.imports == []
    assert any(
        "Unexpected error while processing import statement" in record.getMessage()
        for record in caplog.records
    )