"""Tests for JSON report exporter."""

import json
import tempfile
from pathlib import Path

import pytest

from roboview.schemas.domain.reports import (
    SummaryReport,
    KPISummary,
    ReportMetadata,
    ReportTypeEnum,
)
from roboview.utils.exporters.json_exporter import JSONExporter


def test_json_export_summary_report() -> None:
    """Test exporting a summary report to JSON."""
    # Create a sample report
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Test Project",
            project_root="/test/project",
        ),
        title="Test Summary Report",
        report_type=ReportTypeEnum.SUMMARY,
        summary=KPISummary(
            total_keywords=42,
            unused_keywords=3,
            reusage_rate=65.5,
            documentation_coverage=80.0,
            robocop_issues=12,
            total_files=15,
        ),
        risk_level="LOW",
        health_status="Good project health.",
        robocop_issues_by_category={"Documentation": 5, "Naming": 7},
    )

    # Export to temporary file
    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "report.json"
        JSONExporter.export(report, output_file)

        # Verify file exists
        assert output_file.exists()

        # Load and verify content
        with open(output_file) as f:
            data = json.load(f)

        assert data["title"] == "Test Summary Report"
        assert data["report_type"] == "summary"
        assert data["summary"]["total_keywords"] == 42
        assert data["risk_level"] == "LOW"


def test_json_export_creates_directories() -> None:
    """Test that JSON export creates necessary directories."""
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Test Project",
            project_root="/test/project",
        ),
        title="Test Report",
        report_type=ReportTypeEnum.SUMMARY,
        summary=KPISummary(
            total_keywords=10,
            unused_keywords=0,
            reusage_rate=70.0,
            documentation_coverage=100.0,
            robocop_issues=0,
            total_files=5,
        ),
        risk_level="OPTIMAL",
        health_status="Excellent project health.",
        robocop_issues_by_category={},
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create output path with nested directories
        output_file = Path(temp_dir) / "reports" / "2024" / "report.json"

        # Export should create directories
        JSONExporter.export(report, output_file)

        assert output_file.exists()
        assert output_file.parent.exists()


def test_json_export_valid_json() -> None:
    """Test that exported JSON is valid."""
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Test",
            project_root="/test",
        ),
        title="Test",
        report_type=ReportTypeEnum.SUMMARY,
        summary=KPISummary(
            total_keywords=5,
            unused_keywords=0,
            reusage_rate=80.0,
            documentation_coverage=100.0,
            robocop_issues=0,
            total_files=2,
        ),
        risk_level="OPTIMAL",
        health_status="Excellent project health.",
        robocop_issues_by_category={},
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "report.json"
        JSONExporter.export(report, output_file)

        # Verify JSON is valid by re-parsing
        with open(output_file) as f:
            data = json.load(f)

        # Basic validation
        assert isinstance(data, dict)
        assert "metadata" in data
        assert "title" in data
        assert "summary" in data
