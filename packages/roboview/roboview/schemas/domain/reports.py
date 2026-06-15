"""Domain report schemas for pydantic validation."""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class ReportTypeEnum(str, Enum):
    """Enum for supported report types."""

    SUMMARY = "summary"


class ExportFormatEnum(str, Enum):
    """Enum for supported export formats."""

    HTML = "html"


class ReportMetadata(BaseModel):
    """Metadata for a report."""

    report_id: str = Field(description="Unique identifier for the report", default_factory=lambda: str(uuid4()))
    project_name: str = Field(description="Name of the Robot Framework project")
    project_root: str = Field(description="Root path of the project")
    analysis_date: datetime = Field(description="Date and time of analysis", default_factory=datetime.utcnow)
    roboview_version: str = Field(description="Version of RoboView used", default="0.0.4")
    report_version: str = Field(description="Report format version", default="1.0")
    author: str | None = Field(description="Author of the report", default=None)
    description: str | None = Field(description="Report description", default=None)


class KPISummary(BaseModel):
    """Summary of key performance indicators."""

    total_keywords: int = Field(description="Total number of user-defined keywords")
    unused_keywords: int = Field(description="Number of unused keywords")
    reusage_rate: float = Field(description="Keyword reusage rate as percentage (0-100)")
    documentation_coverage: float = Field(description="Documentation coverage as percentage (0-100)")
    robocop_issues: int = Field(description="Total number of robocop issues")
    total_files: int = Field(description="Total number of robot and resource files")


class Recommendation(BaseModel):
    """A recommendation for improvement."""

    priority: str = Field(description="Priority level (HIGH, MEDIUM, LOW)")
    category: str = Field(description="Category of recommendation")
    message: str = Field(description="Recommendation message")
    details: str | None = Field(description="Additional details", default=None)
    affected_items: list[str] | None = Field(description="List of affected keywords/files", default=None)


class KeywordReportData(BaseModel):
    """Keyword data for report."""

    keyword_id: str = Field(description="Unique identifier for the keyword")
    keyword_name: str = Field(description="Keyword name without prefix")
    file_name: str = Field(description="File where keyword is defined")
    line_number: int | None = Field(description="Line number in file")
    documentation: str | None = Field(description="Keyword documentation")
    usage_count: int = Field(description="Total usage count")
    is_user_defined: bool = Field(description="Whether keyword is user-defined")
    source: str = Field(description="Full file path")


class FileReportData(BaseModel):
    """File data for report."""

    file_name: str = Field(description="Name of the file")
    file_path: str = Field(description="Full path to the file")
    is_resource: bool = Field(description="Whether file is a resource file")
    keywords_defined: int = Field(description="Number of keywords defined")
    keywords_called: int = Field(description="Number of keywords called")
    total_lines: int = Field(description="Total lines in file")


class RobocopIssueData(BaseModel):
    """Robocop issue data for report."""

    issue_id: str = Field(description="Robocop issue ID")
    file_path: str = Field(description="File where issue is found")
    line_number: int | None = Field(description="Line number of issue")
    severity: str = Field(description="Severity level (ERROR, WARNING, INFO)")
    category: str = Field(description="Issue category")
    message: str = Field(description="Issue message")


class DuplicateKeywordPair(BaseModel):
    """Data for a pair of duplicate/similar keywords."""

    keyword1_name: str = Field(description="First keyword name")
    keyword1_file: str = Field(description="File of first keyword")
    keyword2_name: str = Field(description="Second keyword name")
    keyword2_file: str = Field(description="File of second keyword")
    similarity_score: float = Field(description="Similarity score (0-100)")


class Report(BaseModel):
    """Base report model."""

    metadata: ReportMetadata = Field(description="Report metadata")
    title: str = Field(description="Report title")
    report_type: ReportTypeEnum = Field(description="Type of report")
    summary: KPISummary = Field(description="KPI summary")
    recommendations: list[Recommendation] = Field(description="List of recommendations", default_factory=list)


class SummaryReport(Report):
    """Comprehensive summary report combining all analysis data.

    This report is designed for multiple audiences:
    - Business Analysts: Executive overview, KPIs, recommendations
    - Developers: Keyword analysis, code quality issues, refactoring candidates
    - Project Owners: Risk assessment, quality scores, action items
    """

    # Executive Overview
    risk_level: str = Field(description="Overall risk level (CRITICAL, HIGH, MEDIUM, LOW, OPTIMAL)")
    health_status: str = Field(description="Project health status summary")

    # Keyword Analysis
    most_used_keywords: list[KeywordReportData] = Field(
        description="Top 10 most used keywords",
        default_factory=list,
    )
    unused_keywords: list[KeywordReportData] = Field(
        description="Keywords with zero usages (candidates for removal)",
        default_factory=list,
    )
    undocumented_keywords: list[KeywordReportData] = Field(
        description="Keywords missing documentation",
        default_factory=list,
    )
    duplicate_keywords: list[DuplicateKeywordPair] = Field(
        description="Similar/duplicate keyword pairs (refactoring candidates)",
        default_factory=list,
    )

    # File Analysis
    files: list[FileReportData] = Field(
        description="All analyzed files with metrics",
        default_factory=list,
    )
    risk_files: list[str] = Field(
        description="Files with highest issue density",
        default_factory=list,
    )

    # Code Quality
    robocop_issues: list[RobocopIssueData] = Field(
        description="All Robocop issues",
        default_factory=list,
    )
    robocop_issues_by_category: dict[str, int] = Field(
        description="Robocop issues grouped by category",
        default_factory=dict,
    )
    robocop_issues_by_severity: dict[str, int] = Field(
        description="Robocop issues grouped by severity",
        default_factory=dict,
    )

    # Scores
    best_practices_score: float = Field(
        description="Best practices compliance score (0-100)",
        default=0.0,
    )
