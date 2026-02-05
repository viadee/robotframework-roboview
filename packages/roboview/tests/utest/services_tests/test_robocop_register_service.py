import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
from click.exceptions import Exit

from roboview.registries.robocop_registry import RobocopRegistry
from roboview.schemas.domain.robocop import RobocopMessage, RuleCategory
from roboview.services.robocop_register_service import (
    RobocopRegistryService,
    logger,
)


class FakeDirectoryParser:
    def __init__(self, tests: list[Path] | None = None, resources: list[Path] | None = None):
        self._tests = tests or []
        self._resources = resources or []

    def get_test_file_paths(self) -> list[Path]:
        return self._tests

    def get_resource_file_paths(self) -> list[Path]:
        return self._resources


class FakeRangePos:
    def __init__(self, line: int, character: int):
        self.line = line
        self.character = character


class FakeRange:
    def __init__(self, start_line: int, start_char: int, end_line: int, end_char: int):
        self.start = FakeRangePos(start_line, start_char)
        self.end = FakeRangePos(end_line, end_char)


class FakeDiagnostic:
    def __init__(self, rule: str, message: str, severity: str, range_obj: FakeRange, source: str):
        self.rule = rule
        self.message = message
        self.severity = severity
        self.range = range_obj
        self.source = source


class FakeConfigManager:
    def __init__(self, sources: list[str], config: Path | None = None):
        self.sources = sources
        self.config = config


class FakeLinter:
    def __init__(self, diagnostics: list[FakeDiagnostic] | None = None):
        self.diagnostics = diagnostics or []

    def run(self):
        # Simulate the behavior that run() raises Exit when complete
        raise Exit(0)


def _make_paths(tmp_path: Path) -> tuple[Path, Path]:
    robot = tmp_path / "suite.robot"
    resource = tmp_path / "common.resource"
    robot.write_text("*** Keywords ***\nKW\n    No Operation\n", encoding="utf-8")
    resource.write_text("*** Settings ***\n", encoding="utf-8")
    return robot, resource


def test_robocop_registry_service_initial_state(tmp_path, monkeypatch):
    svc = RobocopRegistryService(tmp_path, None)

    monkeypatch.setattr(
        svc,
        "directory_parser",
        FakeDirectoryParser(tests=[], resources=[]),
        raising=True,
    )

    assert svc.get_error_message_list() == []
    assert len(svc.get_robocop_registry()) == 0


def test_initialize_extracts_diagnostics_successfully(tmp_path, monkeypatch):
    robot_file, resource_file = _make_paths(tmp_path)
    svc = RobocopRegistryService(tmp_path, None)

    fake_dir = FakeDirectoryParser(tests=[robot_file], resources=[resource_file])
    monkeypatch.setattr(svc, "directory_parser", fake_dir, raising=True)

    diagnostics = [
        FakeDiagnostic(
            rule="[DOC01] Missing documentation.",
            message="Keyword is missing documentation.",
            severity="WARNING",
            range_obj=FakeRange(2, 1, 2, 10),
            source=str(robot_file),
        ),
        FakeDiagnostic(
            rule="[DOC02] Missing suite documentation.",
            message="Suite is missing documentation.",
            severity="WARNING",
            range_obj=FakeRange(1, 1, 1, 10),
            source=str(resource_file),
        ),
    ]

    fake_linter = FakeLinter(diagnostics)

    monkeypatch.setattr(
        "roboview.services.robocop_register_service.RobocopLinter",
        lambda cfg_mgr: fake_linter,
        raising=True,
    )
    monkeypatch.setattr(
        svc,
        "_get_robocop_config_manager",
        lambda: FakeConfigManager([str(robot_file), str(resource_file)]),
        raising=True,
    )

    svc.initialize()

    messages = svc.get_error_message_list()
    assert len(messages) == 2

    file_names = {m.file_name for m in messages}
    assert "suite.robot" in file_names
    assert "common.resource" in file_names

    robot_msgs = [m for m in messages if m.file_name == "suite.robot"]
    assert len(robot_msgs) == 1
    msg = robot_msgs[0]
    assert isinstance(msg, RobocopMessage)
    assert msg.rule_id == "DOC01"
    assert "Missing documentation" in msg.rule_message
    assert msg.severity == "WARNING"


def test_initialize_logs_error_on_failure(tmp_path, monkeypatch, caplog):
    svc = RobocopRegistryService(tmp_path, None)

    def broken_extract():
        raise RuntimeError("boom")

    monkeypatch.setattr(svc, "_extract_diagnostics", broken_extract, raising=True)

    caplog.set_level(logging.ERROR, logger=logger.name)

    svc.initialize()

    assert any(
        "Failed to initialize file registry" in record.getMessage()
        for record in caplog.records
    )


def test__extract_diagnostics_handles_click_exit_and_registers_messages(tmp_path, monkeypatch):
    robot_file, _ = _make_paths(tmp_path)
    svc = RobocopRegistryService(tmp_path, None)

    fake_dir = FakeDirectoryParser(tests=[robot_file], resources=[])
    monkeypatch.setattr(svc, "directory_parser", fake_dir, raising=True)

    diagnostics = [
        FakeDiagnostic(
            rule="[KW01] Keyword issue.",
            message="Some keyword issue.",
            severity="ERROR",
            range_obj=FakeRange(3, 1, 3, 5),
            source=str(robot_file),
        )
    ]

    fake_linter = FakeLinter(diagnostics)

    monkeypatch.setattr(
        "roboview.services.robocop_register_service.RobocopLinter",
        lambda cfg_mgr: fake_linter,
        raising=True,
    )
    monkeypatch.setattr(
        svc,
        "_get_robocop_config_manager",
        lambda: FakeConfigManager([str(robot_file)]),
        raising=True,
    )

    svc._extract_diagnostics()

    messages = svc.get_error_message_list()
    assert len(messages) == 1
    assert messages[0].rule_id == "KW01"
    assert messages[0].file_name == robot_file.name


def test__extract_diagnostics_handles_general_exception(tmp_path, monkeypatch, caplog):
    svc = RobocopRegistryService(tmp_path, None)

    # Create a fake linter that raises during run()
    class BrokenLinter:
        def __init__(self, config_manager):
            self.diagnostics = []

        def run(self):
            raise RuntimeError("boom")

    monkeypatch.setattr(
        "roboview.services.robocop_register_service.RobocopLinter",
        BrokenLinter,
        raising=True,
    )
    monkeypatch.setattr(
        svc,
        "_get_robocop_config_manager",
        lambda: FakeConfigManager([]),
        raising=True,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    svc._extract_diagnostics()

    assert any(
        "Failed to extract diagnostics from Robocop run" in record.getMessage()
        for record in caplog.records
    )


def test__extract_diagnostics_handles_no_diagnostics(tmp_path, monkeypatch):
    robot_file, _ = _make_paths(tmp_path)
    svc = RobocopRegistryService(tmp_path, None)

    fake_dir = FakeDirectoryParser(tests=[robot_file], resources=[])
    monkeypatch.setattr(svc, "directory_parser", fake_dir, raising=True)

    # Linter with no diagnostics
    fake_linter = FakeLinter(diagnostics=[])

    monkeypatch.setattr(
        "roboview.services.robocop_register_service.RobocopLinter",
        lambda cfg_mgr: fake_linter,
        raising=True,
    )
    monkeypatch.setattr(
        svc,
        "_get_robocop_config_manager",
        lambda: FakeConfigManager([str(robot_file)]),
        raising=True,
    )

    svc._extract_diagnostics()

    assert len(svc.get_error_message_list()) == 0


@pytest.mark.parametrize(
    "rule_text,expected",
    [
        ("[DOC01] Missing documentation.", "DOC01"),
        ("[ARG02] Something else", "ARG02"),
        ("No brackets here", ""),
    ],
)
def test__extract_rule_id(rule_text, expected):
    assert RobocopRegistryService._extract_rule_id(rule_text) == expected


@pytest.mark.parametrize(
    "rule_text,expected",
    [
        ("[DOC01] Missing documentation.", RuleCategory.DOC),
        ("[ARG10] Some argument issue", RuleCategory.ARG),
        ("[SPC02] Spacing issue", RuleCategory.SPC),
        ("[XYZ01] Unknown", ""),
        ("No code here", ""),
    ],
)
def test__extract_rule_category(rule_text, expected):
    assert RobocopRegistryService._extract_rule_category(rule_text) == expected


def test__get_robocop_config_manager_without_config_file(tmp_path, monkeypatch):
    robot_file, resource_file = _make_paths(tmp_path)
    svc = RobocopRegistryService(tmp_path, None)

    fake_dir = FakeDirectoryParser(tests=[robot_file], resources=[resource_file])
    monkeypatch.setattr(svc, "directory_parser", fake_dir, raising=True)

    with patch("roboview.services.robocop_register_service.ConfigManager") as mock_cm:
        svc._get_robocop_config_manager()

        mock_cm.assert_called_once()
        call_args = mock_cm.call_args
        assert "sources" in call_args.kwargs
        assert str(robot_file) in call_args.kwargs["sources"]
        assert str(resource_file) in call_args.kwargs["sources"]
        assert "config" not in call_args.kwargs


def test__get_robocop_config_manager_with_valid_config_file(tmp_path, monkeypatch):
    robot_file, resource_file = _make_paths(tmp_path)
    config_file = tmp_path / ".robocop"
    config_file.write_text("", encoding="utf-8")

    svc = RobocopRegistryService(tmp_path, config_file)

    fake_dir = FakeDirectoryParser(tests=[robot_file], resources=[resource_file])
    monkeypatch.setattr(svc, "directory_parser", fake_dir, raising=True)

    # Mock _check_robocop_config to return True
    monkeypatch.setattr(svc, "_check_robocop_config", lambda: True, raising=True)

    with patch("roboview.services.robocop_register_service.ConfigManager") as mock_cm:
        svc._get_robocop_config_manager()

        mock_cm.assert_called_once()
        call_args = mock_cm.call_args
        assert call_args.kwargs["config"] == config_file


def test__get_robocop_config_manager_with_invalid_config_file(tmp_path, monkeypatch):
    robot_file, _ = _make_paths(tmp_path)
    config_file = tmp_path / ".robocop"
    config_file.write_text("", encoding="utf-8")

    svc = RobocopRegistryService(tmp_path, config_file)

    fake_dir = FakeDirectoryParser(tests=[robot_file], resources=[])
    monkeypatch.setattr(svc, "directory_parser", fake_dir, raising=True)

    # Mock _check_robocop_config to return False
    monkeypatch.setattr(svc, "_check_robocop_config", lambda: False, raising=True)

    with patch("roboview.services.robocop_register_service.ConfigManager") as mock_cm:
        svc._get_robocop_config_manager()

        call_args = mock_cm.call_args
        assert call_args is None


def test__check_robocop_config_valid_config(tmp_path, monkeypatch):
    config_file = tmp_path / ".robocop"
    config_file.write_text("", encoding="utf-8")

    svc = RobocopRegistryService(tmp_path, config_file)

    with patch("roboview.services.robocop_register_service.ConfigManager") as mock_cm:
        # Mock ConfigManager to not raise
        mock_cm.return_value = MagicMock()

        result = svc._check_robocop_config()

        assert result is True


def test__check_robocop_config_invalid_config_raises_exit(tmp_path, caplog):
    config_file = tmp_path / ".robocop"
    config_file.write_text("", encoding="utf-8")

    svc = RobocopRegistryService(tmp_path, config_file)

    with patch("roboview.services.robocop_register_service.ConfigManager") as mock_cm:
        # Mock ConfigManager to raise Exit
        mock_cm.side_effect = Exit(1)

        caplog.set_level(logging.WARNING, logger=logger.name)

        result = svc._check_robocop_config()

        assert result is False
        assert any(
            "deprecated" in record.getMessage().lower()
            for record in caplog.records
        )


def test_extract_code_snippet_happy_path(tmp_path):
    file_path = tmp_path / "file.robot"
    file_path.write_text(
        "line1\n"
        "KW    Arg\n"
        "line3\n",
        encoding="utf-8",
    )

    snippet = RobocopRegistryService.extract_code_snippet(
        file_path=file_path,
        line=2,
        column=1,
        end_line=2,
        end_column=5,
        context_lines=1,
    )

    assert "lines" in snippet
    assert snippet["error_line"] == 2
    assert snippet["highlight_start"] == 0
    assert snippet["highlight_end"] == 4
    assert snippet["highlighted_text"] != ""


def test_extract_code_snippet_file_missing(tmp_path):
    file_path = tmp_path / "does_not_exist.robot"

    snippet = RobocopRegistryService.extract_code_snippet(
        file_path=file_path,
        line=1,
        column=1,
    )

    assert snippet == {}


def test_format_code_snippet_empty_returns_empty_string():
    result = RobocopRegistryService.format_code_snippet({})
    assert result == ""


def test_format_code_snippet_formats_lines_and_marker():
    snippet = {
        "lines": [
            {"line_number": 1, "content": "line1", "is_error": False},
            {"line_number": 2, "content": "KW    Arg", "is_error": True},
            {"line_number": 3, "content": "line3", "is_error": False},
        ],
        "error_line": 2,
        "error_column": 1,
        "highlight_start": 0,
        "highlight_end": 2,
        "highlighted_text": "KW",
    }

    formatted = RobocopRegistryService.format_code_snippet(snippet)

    assert "1 | line1" in formatted
    assert "2 | KW    Arg" in formatted
    assert "^" in formatted


def test_get_error_message_list_and_registry_accessor(tmp_path):
    svc = RobocopRegistryService(tmp_path, None)
    reg = svc.get_robocop_registry()

    assert isinstance(reg, RobocopRegistry)
    assert reg is svc.robocop_registry