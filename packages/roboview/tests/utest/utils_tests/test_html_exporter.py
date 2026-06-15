"""Tests for HTML report exporter."""

import tempfile
from pathlib import Path

import pytest

from roboview.schemas.domain.reports import (
    SummaryReport,
    KPISummary,
    ReportMetadata,
    ReportTypeEnum,
    Recommendation,
)
from roboview.utils.exporters.html_exporter import HTMLExporter


def test_html_export_summary_report() -> None:
    """Test exporting a summary report to HTML."""
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Test Project",
            project_root="/test/project",
            author="Test Author",
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
        recommendations=[
            Recommendation(
                priority="HIGH",
                category="Documentation",
                message="Add documentation to 5 keywords",
            ),
            Recommendation(
                priority="MEDIUM",
                category="Code Quality",
                message="Address robocop issues",
            ),
        ],
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "report.html"
        HTMLExporter.export(report, output_file)

        # Verify file exists and contains HTML
        assert output_file.exists()
        content = output_file.read_text()
        assert "<!DOCTYPE html>" in content
        assert "Test Summary Report" in content
        assert "Key Performance Indicators" in content
        assert "42" in content  # total_keywords


def test_html_export_with_best_practices() -> None:
    """Test exporting a summary report with best practices score."""
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Quality Test",
            project_root="/test/project",
        ),
        title="Quality Assessment Report",
        report_type=ReportTypeEnum.SUMMARY,
        summary=KPISummary(
            total_keywords=50,
            unused_keywords=5,
            reusage_rate=70.0,
            documentation_coverage=85.0,
            robocop_issues=20,
            total_files=20,
        ),
        risk_level="MEDIUM",
        health_status="Moderate project health.",
        robocop_issues_by_category={"Documentation": 8, "Naming": 7, "Spacing": 5},
        robocop_issues_by_severity={"ERROR": 5, "WARNING": 10, "INFO": 5},
        best_practices_score=82.5,
        risk_files=["/test/file1.robot", "/test/file2.robot"],
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "quality.html"
        HTMLExporter.export(report, output_file)

        assert output_file.exists()
        content = output_file.read_text()
        assert "Quality Assessment Report" in content


def test_html_export_contains_styles() -> None:
    """Test that HTML export includes styling."""
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Test",
            project_root="/test",
        ),
        title="Styled Report",
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
        output_file = Path(temp_dir) / "styled.html"
        HTMLExporter.export(report, output_file)

        content = output_file.read_text()
        assert "<style>" in content
        assert "background:" in content
        assert "color:" in content
        assert "font-family:" in content


def test_html_export_creates_directories() -> None:
    """Test that HTML export creates necessary directories."""
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Test",
            project_root="/test",
        ),
        title="Test",
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
        output_file = Path(temp_dir) / "reports" / "2024" / "report.html"
        HTMLExporter.export(report, output_file)

        assert output_file.exists()
        assert output_file.parent.exists()


def test_html_export_kpi_values() -> None:
    """Test that HTML export includes correct KPI values."""
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="KPI Test",
            project_root="/test",
        ),
        title="KPI Report",
        report_type=ReportTypeEnum.SUMMARY,
        summary=KPISummary(
            total_keywords=123,
            unused_keywords=7,
            reusage_rate=82.5,
            documentation_coverage=91.3,
            robocop_issues=42,
            total_files=25,
        ),
        risk_level="LOW",
        health_status="Good project health.",
        robocop_issues_by_category={},
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "kpi.html"
        HTMLExporter.export(report, output_file)

        content = output_file.read_text()
        assert "123" in content  # total_keywords
        assert "7" in content    # unused_keywords
        assert "82.5" in content  # reusage_rate
        assert "91.3" in content  # documentation_coverage
        assert "42" in content   # robocop_issues
        assert "25" in content   # total_files


def test_html_export_recommendations() -> None:
    """Test that HTML export includes recommendations."""
    recommendations = [
        Recommendation(
            priority="HIGH",
            category="Documentation",
            message="Add documentation to 5 keywords",
            details="Critical for maintainability",
            affected_items=["Keyword1", "Keyword2", "Keyword3"],
        ),
        Recommendation(
            priority="MEDIUM",
            category="Code Quality",
            message="Fix robocop issues",
            details="Address naming conventions",
        ),
        Recommendation(
            priority="LOW",
            category="Performance",
            message="Optimize keyword reusability",
        ),
    ]

    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Rec Test",
            project_root="/test",
        ),
        title="Recommendations Report",
        report_type=ReportTypeEnum.SUMMARY,
        summary=KPISummary(
            total_keywords=30,
            unused_keywords=3,
            reusage_rate=65.0,
            documentation_coverage=75.0,
            robocop_issues=10,
            total_files=10,
        ),
        risk_level="MEDIUM",
        health_status="Moderate project health.",
        robocop_issues_by_category={},
        recommendations=recommendations,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "rec.html"
        HTMLExporter.export(report, output_file)

        content = output_file.read_text()
        assert "Add documentation to 5 keywords" in content
        assert "Fix robocop issues" in content
        assert "Optimize keyword reusability" in content
        assert "HIGH" in content or "high" in content.lower()
        assert "MEDIUM" in content or "medium" in content.lower()


def test_html_export_is_valid_html() -> None:
    """Test that exported HTML is valid."""
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Valid Test",
            project_root="/test",
        ),
        title="Valid HTML Report",
        report_type=ReportTypeEnum.SUMMARY,
        summary=KPISummary(
            total_keywords=20,
            unused_keywords=2,
            reusage_rate=75.0,
            documentation_coverage=90.0,
            robocop_issues=5,
            total_files=10,
        ),
        risk_level="LOW",
        health_status="Good project health.",
        robocop_issues_by_category={},
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "valid.html"
        HTMLExporter.export(report, output_file)

        content = output_file.read_text()
        # Basic HTML structure validation
        assert content.startswith("<!DOCTYPE html>")
        assert "<html" in content
        assert "</html>" in content
        assert "<head>" in content
        assert "</head>" in content
        assert "<body>" in content
        assert "</body>" in content
        assert "<style>" in content
        assert "</style>" in content
