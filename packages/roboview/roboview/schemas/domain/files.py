"""Domain Robot Framework file schema for pydantic validation."""

from pydantic import BaseModel, Field


class FileProperties(BaseModel):
    """Schema containing Robot Framework file properties."""

    file_name: str = Field(description="Name of the Robot Framework file")
    path: str = Field(description="Path of the Robot Framework file as POSIX")
    is_resource: bool = Field(description="Whether the file is a .resource file")
    initialized_keywords: list[str] | None = Field(description="List of initialized keywords", default=None)
    called_keywords: list[str] | None = Field(description="List of called keywords", default=None)
    imported_files: list[str] | None = Field(description="List of imported resource files or Libraries", default=None)


class FileUsage(BaseModel):
    """Schema for displaying where and how often a Keyword is used in a specific file."""

    file_name: str = Field(description="Name of the Robot Framework file")
    path: str = Field(description="Path of the Robot Framework file as POSIX")
    usages: int = Field(description="How often the requested keyword is used in this particular file")


class SelectionFiles(BaseModel):
    """Schema for file selection in RoboView."""

    file_name: str = Field(description="Name of the Robot Framework file")
    path: str = Field(description="Path of the Robot Framework file as POSIX")
