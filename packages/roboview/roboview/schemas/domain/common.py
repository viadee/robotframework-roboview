"""Common domain schemas for pydantic validation."""

from enum import Enum


class LibraryType(Enum):
    """Supported Robot Framework libraries."""

    BROWSER = "Browser"
    SELENIUM = "SeleniumLibrary"
    BUILTIN = "BuiltIn"
    DATABASE = "DatabaseLibrary"


class FileType(Enum):
    """Supported Robot Framework files."""

    ROBOT = "robot"
    RESOURCE = "resource"


class KeywordType(Enum):
    """Supported Robot Framework keyword types."""

    INITIALIZED = "initialized"
    CALLED = "called"
