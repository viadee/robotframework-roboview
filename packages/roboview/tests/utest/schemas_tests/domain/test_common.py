import pytest

from roboview.schemas.domain.common import BuiltinLibraryType, ExternalLibraryType, FileType, KeywordType


def test_external_library_type_values_and_members():
    assert ExternalLibraryType.BROWSER.value == "Browser"
    assert ExternalLibraryType.SELENIUM.value == "SeleniumLibrary"
    assert ExternalLibraryType.DATABASE.value == "DatabaseLibrary"
    assert ExternalLibraryType.APPIUM.value == "AppiumLibrary"
    assert ExternalLibraryType.REQUESTS.value == "RequestsLibrary"

    assert set(ExternalLibraryType.__members__.keys()) == {
        "BROWSER",
        "SELENIUM",
        "DATABASE",
        "APPIUM",
        "REQUESTS",
    }


def test_builtin_library_type_values_and_members():
    assert BuiltinLibraryType.BUILTIN.value == "BuiltIn"
    assert BuiltinLibraryType.COLLECTIONS.value == "Collections"
    assert BuiltinLibraryType.DATETIME.value == "DateTime"
    assert BuiltinLibraryType.OPERATINGSYSTEM.value == "OperatingSystem"

    assert set(BuiltinLibraryType.__members__.keys()) == {
        "BUILTIN",
        "COLLECTIONS",
        "DATETIME",
        "DIALOGS",
        "OPERATINGSYSTEM",
        "PROCESS",
        "SCREENSHOT",
        "STRING",
        "TELNET",
        "XML",
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


def test_external_library_type_from_value_roundtrip():
    assert ExternalLibraryType("Browser") is ExternalLibraryType.BROWSER
    assert ExternalLibraryType("SeleniumLibrary") is ExternalLibraryType.SELENIUM
    assert ExternalLibraryType("DatabaseLibrary") is ExternalLibraryType.DATABASE


def test_builtin_library_type_from_value_roundtrip():
    assert BuiltinLibraryType("BuiltIn") is BuiltinLibraryType.BUILTIN
    assert BuiltinLibraryType("Collections") is BuiltinLibraryType.COLLECTIONS


def test_file_type_from_value_roundtrip():
    assert FileType("robot") is FileType.ROBOT
    assert FileType("resource") is FileType.RESOURCE


def test_keyword_type_from_value_roundtrip():
    assert KeywordType("initialized") is KeywordType.INITIALIZED
    assert KeywordType("called") is KeywordType.CALLED


def test_invalid_external_library_type_raises_value_error():
    with pytest.raises(ValueError):
        ExternalLibraryType("UnknownLib")


def test_invalid_builtin_library_type_raises_value_error():
    with pytest.raises(ValueError):
        BuiltinLibraryType("UnknownLib")


def test_invalid_file_type_raises_value_error():
    with pytest.raises(ValueError):
        FileType("txt")


def test_invalid_keyword_type_raises_value_error():
    with pytest.raises(ValueError):
        KeywordType("other")