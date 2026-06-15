"""Tests for PDF report exporter."""

import tempfile
from pathlib import Path

import pytest

from roboview.schemas.domain.reports import (
    SummaryReport,
    KPISummary,
    ReportMetadata,
    ReportTypeEnum,
    RobocopIssueData,
)
from roboview.utils.exporters.pdf_exporter import PDFExporter


def test_pdf_export_summary_report() -> None:
    """Test exporting a summary report to PDF."""
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

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "report.pdf"
        PDFExporter.export(report, output_file)

        # Verify file exists and has content
        assert output_file.exists()
        assert output_file.stat().st_size > 1000  # PDF should be at least 1KB


def test_pdf_export_with_best_practices() -> None:
    """Test exporting a summary report with best practices score to PDF."""
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Test Project",
            project_root="/test/project",
        ),
        title="Test Quality Assessment",
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
        output_file = Path(temp_dir) / "quality.pdf"
        PDFExporter.export(report, output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 1000


def test_pdf_export_creates_directories() -> None:
    """Test that PDF export creates necessary directories."""
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
        output_file = Path(temp_dir) / "reports" / "2024" / "report.pdf"
        PDFExporter.export(report, output_file)

        assert output_file.exists()
        assert output_file.parent.exists()


def test_pdf_export_with_author() -> None:
    """Test PDF export includes author information."""
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Test Project",
            project_root="/test/project",
            author="John Doe",
        ),
        title="Test Report",
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
        output_file = Path(temp_dir) / "report.pdf"
        PDFExporter.export(report, output_file)

        assert output_file.exists()
        assert output_file.stat().st_size > 0


def test_pdf_export_all_risk_levels() -> None:
    """Test PDF export with all risk levels."""
    for risk_level in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "OPTIMAL"]:
        report = SummaryReport(
            metadata=ReportMetadata(
                project_name="Test Project",
                project_root="/test/project",
            ),
            title=f"Test {risk_level}",
            report_type=ReportTypeEnum.SUMMARY,
            summary=KPISummary(
                total_keywords=30,
                unused_keywords=3,
                reusage_rate=65.0,
                documentation_coverage=75.0,
                robocop_issues=10,
                total_files=12,
            ),
            risk_level=risk_level,
            health_status="Project health status.",
            robocop_issues_by_category={},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / f"report_{risk_level}.pdf"
            PDFExporter.export(report, output_file)

            assert output_file.exists()
