"""Schemas for keyword usage functionality."""

from pydantic import BaseModel, Field
from roboview.schemas.domain.files import FileUsage
from roboview.schemas.domain.keywords import KeywordUsage


class InitializedKeywordsResponse(BaseModel):
    """Response model to fetch initialized keywords in a Robot Framework file."""

    initialized_keywords: list[KeywordUsage] = Field(description="List of all initialized keywords")


class CalledKeywordsResponse(BaseModel):
    """Response model to fetch called keywords in a Robot Framework file."""

    called_keywords: list[KeywordUsage] = Field(description="List of all called keywords")


class KeywordUsageResourceResponse(BaseModel):
    """Response model to fetch the keyword usage across all resource files."""

    keyword_usage_resource: list[FileUsage] = Field(description="Resource files, where the target keyword is used")


class KeywordUsageRobotResponse(BaseModel):
    """Response model to fetch the keyword usage across all resource files."""

    keyword_usage_robot: list[FileUsage] = Field(description="Resource files, where the target keyword is used")


class KeywordsWithoutDocResponse(BaseModel):
    """Response model to fetch the keywords without documentation."""

    keywords_wo_documentation: list[KeywordUsage] = Field(
        description="List containing keywords that have an empty [Documentation]"
    )


class KeywordsWithoutUsagesResponse(BaseModel):
    """Response model to fetch the keywords without usages."""

    keywords_wo_usages: list[KeywordUsage] = Field(description="List of keywords that have no usages")
