import pytest
import logging

from pathlib import Path

from roboview.utils.directory_parsing import DirectoryParser


def test_get_test_file_paths_finds_robot_files(tmp_path: Path):
    (tmp_path / "suite1.robot").write_text("*** Test Cases ***")
    (tmp_path / "suite2.robot").write_text("*** Test Cases ***")
    (tmp_path / "not_robot.txt").write_text("ignore me")
    subdir = tmp_path / "sub"
    subdir.mkdir()
    (subdir / "nested.robot").write_text("*** Test Cases ***")

    parser = DirectoryParser(tmp_path)

    result = parser.get_test_file_paths()

    names = sorted(p.name for p in result)
    assert names == ["nested.robot", "suite1.robot", "suite2.robot"]


def test_get_resource_file_paths_finds_resource_files(tmp_path: Path):
    (tmp_path / "common.resource").write_text("*** Keywords ***")
    (tmp_path / "other.resource").write_text("*** Keywords ***")
    (tmp_path / "ignore.robot").write_text("*** Test Cases ***")
    subdir = tmp_path / "sub"
    subdir.mkdir()
    (subdir / "nested.resource").write_text("*** Keywords ***")

    parser = DirectoryParser(tmp_path)

    result = parser.get_resource_file_paths()

    names = sorted(p.name for p in result)
    assert names == ["common.resource", "nested.resource", "other.resource"]


def test_get_test_file_paths_propagates_oserror_and_logs(caplog, monkeypatch, tmp_path: Path):
    parser = DirectoryParser(tmp_path)

    class FakePath(Path):
        _flavour = Path(tmp_path). _flavour  # type: ignore[attr-defined]

        def rglob(self, pattern):
            raise OSError("permission denied")

    fake_root = FakePath(str(tmp_path))

    parser.project_root_path = fake_root  # type: ignore[assignment]

    caplog.set_level(logging.ERROR)

    with pytest.raises(OSError):
        parser.get_test_file_paths()

    assert "Error while searching for .robot files" in caplog.text


def test_get_resource_file_paths_propagates_oserror_and_logs(caplog, monkeypatch, tmp_path: Path):
    parser = DirectoryParser(tmp_path)

    class FakePath(Path):
        _flavour = Path(tmp_path). _flavour  # type: ignore[attr-defined]

        def rglob(self, pattern):
            raise OSError("permission denied")

    fake_root = FakePath(str(tmp_path))

    parser.project_root_path = fake_root  # type: ignore[assignment]

    caplog.set_level(logging.ERROR)

    with pytest.raises(OSError):
        parser.get_resource_file_paths()

    assert "Error while searching for .resource files" in caplog.text