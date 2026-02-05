import pytest

from roboview.schemas.domain.common import LibraryType, FileType, KeywordType


def test_library_type_values_and_members():
    assert LibraryType.BROWSER.value == "Browser"
    assert LibraryType.SELENIUM.value == "SeleniumLibrary"
    assert LibraryType.BUILTIN.value == "BuiltIn"
    assert LibraryType.DATABASE.value == "DatabaseLibrary"

    assert set(LibraryType.__members__.keys()) == {
        "BROWSER",
        "SELENIUM",
        "BUILTIN",
        "DATABASE",
    }


def test_file_type_values_and_members():
    assert FileType.ROBOT.value == "robot"
    assert FileType.RESOURCE.value == "resource"

    assert set(FileType.__members__.keys()) == {
        "ROBOT",
        "RESOURCE",
    }


def test_keyword_type_values_and_members():
    assert KeywordType.INITIALIZED.value == "initialized"
    assert KeywordType.CALLED.value == "called"

    assert set(KeywordType.__members__.keys()) == {
        "INITIALIZED",
        "CALLED",
    }


def test_library_type_from_value_roundtrip():
    assert LibraryType("Browser") is LibraryType.BROWSER
    assert LibraryType("SeleniumLibrary") is LibraryType.SELENIUM
    assert LibraryType("BuiltIn") is LibraryType.BUILTIN
    assert LibraryType("DatabaseLibrary") is LibraryType.DATABASE


def test_file_type_from_value_roundtrip():
    assert FileType("robot") is FileType.ROBOT
    assert FileType("resource") is FileType.RESOURCE


def test_keyword_type_from_value_roundtrip():
    assert KeywordType("initialized") is KeywordType.INITIALIZED
    assert KeywordType("called") is KeywordType.CALLED


def test_invalid_library_type_raises_value_error():
    with pytest.raises(ValueError):
        LibraryType("UnknownLib")


def test_invalid_file_type_raises_value_error():
    with pytest.raises(ValueError):
        FileType("txt")


def test_invalid_keyword_type_raises_value_error():
    with pytest.raises(ValueError):
        KeywordType("other")