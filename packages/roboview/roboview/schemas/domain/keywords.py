"""Domain keyword schemas for pydantic validation."""

from uuid import uuid4

from pydantic import BaseModel, Field


class KeywordProperties(BaseModel):
    """Schema containing Robot Framework keyword properties."""

    keyword_id: str = Field(description="Unique identifier for the keyword", default_factory=lambda: str(uuid4()))
    file_name: str = Field(description="Name of the file, where the keyword is defined")
    keyword_name_without_prefix: str = Field(description="Name of the keyword without prefix")
    keyword_name_with_prefix: str = Field(description="Name of the keyword with prefix")
    description: str | None = Field(description="Natural language description of the keyword", default=None)
    is_user_defined: bool = Field(description="Whether the keyword is a user defined keyword")
    code: str = Field(description="Robot Framework code of the keyword")
    source: str = Field(description="Path of the file, where the keyword is defined as POSIX")
    validation_str_without_prefix: str = Field(description="Validation string without prefix")
    validation_str_with_prefix: str = Field(description="Validation string with prefix")
    called_keywords: list[str] | None = Field(
        description="List of keywords that are called by the actual Keyword", default=[]
    )


class KeywordUsage(BaseModel):
    """Schema containing properties to display the Robot Framework keyword usage."""

    keyword_id: str = Field(description="Unique identifier for the keyword")
    file_name: str = Field(description="Name of the file, where the keyword is defined")
    keyword_name_without_prefix: str = Field(description="Name of the keyword without prefix")
    keyword_name_with_prefix: str = Field(description="Name of the keyword with prefix")
    documentation: str | None = Field(description="Documentation of the keyword", default=None)
    source: str = Field(description="Path of the file, where the keyword is defined as POSIX")
    file_usages: int = Field(description="Usage of the keyword, in the selected file")
    total_usages: int = Field(description="Total usage of the keyword across the whole project")


class SimilarKeyword(BaseModel):
    """Schema for displaying the n most similar keywords w.r.t to a target keyword."""

    keyword_id: str = Field(description="Unique identifier for the keyword")
    keyword_name_without_prefix: str = Field(description="Name of the keyword without prefix")
    keyword_name_with_prefix: str = Field(description="Name of the keyword with prefix")
    source: str = Field(description="Path of the file, where the keyword is defined as POSIX")
    score: float = Field(description="Similarity score as float on a scale from 0-100")
