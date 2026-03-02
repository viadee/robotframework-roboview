"""Common domain schemas for pydantic validation."""

from enum import Enum


class ExternalLibraryType(Enum):
    """Supported external Robot Framework libraries."""

    BROWSER = "Browser"
    SELENIUM = "SeleniumLibrary"
    DATABASE = "DatabaseLibrary"
    APPIUM = "AppiumLibrary"
    REQUESTS = "RequestsLibrary"


class BuiltinLibraryType(Enum):
    """Supported Robot Framework BuiltIn libraries."""

    BUILTIN = "BuiltIn"
    COLLECTIONS = "Collections"
    DATETIME = "DateTime"
    DIALOGS = "Dialogs"
    OPERATINGSYSTEM = "OperatingSystem"
    PROCESS = "Process"
    SCREENSHOT = "Screenshot"
    STRING = "String"
    TELNET = "Telnet"
    XML = "XML"


class FileType(Enum):
    """Supported Robot Framework files."""

    ROBOT = "robot"
    RESOURCE = "resource"


class KeywordType(Enum):
    """Supported Robot Framework keyword types."""

    INITIALIZED = "initialized"
    CALLED = "called"
