"""DTOs for report endpoints."""

from enum import StrEnum

from pydantic import BaseModel, Field


class ReportTypeEnum(StrEnum):
    """Enum for report types."""

    SUMMARY = "summary"


class ExportFormatEnum(StrEnum):
    """Enum for export formats."""

    HTML = "html"


class GenerateReportRequest(BaseModel):
    """Request model for generating a report."""

    author: str | None = Field(description="Author of the report", default=None)
    project_root_dir: str | None = Field(description="Project root directory path", default=None)


class ReportStatusResponse(BaseModel):
    """Response model for report status."""

    report_id: str = Field(description="Unique report ID")
    status: str = Field(description="Status of report generation (generating, completed, failed)")
    download_url: str | None = Field(description="URL to download report", default=None)
    error_message: str | None = Field(description="Error message if generation failed", default=None)
    file_size: int | None = Field(description="File size in bytes", default=None)
    created_at: str = Field(description="Timestamp when report was created")


class ReportMetadataResponse(BaseModel):
    """Response model for report metadata."""

    report_id: str = Field(description="Unique report ID")
    report_type: str = Field(description="Type of report")
    export_format: str = Field(description="Export format")
    created_at: str = Field(description="Timestamp when report was created")
    project_name: str = Field(description="Project name")
    file_size: int | None = Field(description="File size in bytes", default=None)
    download_url: str | None = Field(description="URL to download report", default=None)
