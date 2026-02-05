"""Overview page schemas for pydantic validation."""

from pydantic import BaseModel, Field
from roboview.schemas.domain.keywords import KeywordUsage
from roboview.schemas.domain.robocop import IssueSummary


class KPIResponse(BaseModel):
    """Response schema containing Roboview KPIs."""

    num_user_keywords: int = Field(description="Number of user defined keywords", default=0)
    num_unused_keywords: int = Field(description="Number of unused keywords", default=0)
    keyword_reusage_rate: float = Field(description="Keyword reusage rate", default=0.0)
    num_robocop_issues: int = Field(description="Number of robocop error messages", default=0)
    documentation_coverage: float = Field(description="Ratio of keywords with documentation", default=0.0)
    num_rf_files: int = Field(description="Number of Robot Framework files", default=0)


class MostUsedKeywordsResponse(BaseModel):
    """Response schema for most used keywords."""

    most_used_user_keywords: list[KeywordUsage] = Field(description="List of most used user defined keywords")
    most_used_external_keywords: list[KeywordUsage] = Field(
        description="List of most used external or builtin Keywords"
    )


class RobocopIssueSummaryResponse(BaseModel):
    """Response schema for Robocop issue summary."""

    robocop_issue_summary: list[IssueSummary] = Field(description="List of most occurring issue categories")
