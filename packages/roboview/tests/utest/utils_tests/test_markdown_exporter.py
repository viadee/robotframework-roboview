"""Tests for Markdown report exporter."""

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
from roboview.utils.exporters.markdown_exporter import MarkdownExporter


def test_markdown_export_summary_report() -> None:
    """Test exporting summary report to Markdown."""
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Test Project",
            project_root="/test/project",
            author="Test Author",
        ),
        title="Summary Report",
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
        output_file = Path(temp_dir) / "report.md"
        MarkdownExporter.export(report, output_file)

        # Verify file exists
        assert output_file.exists()

        # Verify content
        content = output_file.read_text()
        assert "# Summary Report" in content
        assert "## Report Information" in content
        assert "## Key Performance Indicators" in content
        assert "Test Project" in content


def test_markdown_export_contains_kpi_table() -> None:
    """Test that Markdown export includes KPI table."""
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="KPI Test",
            project_root="/test",
        ),
        title="KPI Report",
        report_type=ReportTypeEnum.SUMMARY,
        summary=KPISummary(
            total_keywords=100,
            unused_keywords=5,
            reusage_rate=80.0,
            documentation_coverage=95.0,
            robocop_issues=3,
            total_files=20,
        ),
        risk_level="OPTIMAL",
        health_status="Excellent project health.",
        robocop_issues_by_category={},
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "kpi.md"
        MarkdownExporter.export(report, output_file)

        content = output_file.read_text()
        # Check for table markers
        assert "|" in content  # Table character
        assert "100" in content  # total_keywords
        assert "80" in content   # reusage_rate
        assert "95" in content   # documentation_coverage


def test_markdown_export_contains_risk_assessment() -> None:
    """Test that Markdown export includes risk assessment."""
    for risk_level in ["OPTIMAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"]:
        report = SummaryReport(
            metadata=ReportMetadata(
                project_name="Risk Test",
                project_root="/test",
            ),
            title=f"Risk Report {risk_level}",
            report_type=ReportTypeEnum.SUMMARY,
            summary=KPISummary(
                total_keywords=30,
                unused_keywords=2,
                reusage_rate=70.0,
                documentation_coverage=80.0,
                robocop_issues=8,
                total_files=12,
            ),
            risk_level=risk_level,
            health_status="Project health status.",
            robocop_issues_by_category={},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / f"risk_{risk_level}.md"
            MarkdownExporter.export(report, output_file)

            content = output_file.read_text()
            assert "## Risk Assessment" in content
            assert f"**{risk_level}**" in content


def test_markdown_export_recommendations_by_priority() -> None:
    """Test that Markdown export groups recommendations by priority."""
    recommendations = [
        Recommendation(
            priority="HIGH",
            category="Documentation",
            message="Add documentation to 5 keywords",
        ),
        Recommendation(
            priority="MEDIUM",
            category="Code Quality",
            message="Fix robocop issues",
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
        output_file = Path(temp_dir) / "rec.md"
        MarkdownExporter.export(report, output_file)

        content = output_file.read_text()
        assert "## Recommendations" in content
        assert "### 🔴 High Priority" in content
        assert "### 🟡 Medium Priority" in content
        assert "### 🔵 Low Priority" in content
        assert "Add documentation to 5 keywords" in content
        assert "Fix robocop issues" in content
        assert "Optimize keyword reusability" in content


def test_markdown_export_robocop_issues() -> None:
    """Test that Markdown export includes robocop issues."""
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Robocop Test",
            project_root="/test",
        ),
        title="Robocop Report",
        report_type=ReportTypeEnum.SUMMARY,
        summary=KPISummary(
            total_keywords=40,
            unused_keywords=3,
            reusage_rate=72.0,
            documentation_coverage=82.0,
            robocop_issues=15,
            total_files=14,
        ),
        risk_level="MEDIUM",
        health_status="Moderate project health.",
        robocop_issues_by_category={"Documentation": 8, "Naming": 5, "Spacing": 2},
        robocop_issues_by_severity={"ERROR": 5, "WARNING": 8, "INFO": 2},
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "robocop.md"
        MarkdownExporter.export(report, output_file)

        content = output_file.read_text()
        assert "## Code Quality Audit" in content
        assert "### Issues by Category" in content
        assert "Documentation" in content
        assert "### Issues by Severity" in content
        assert "ERROR" in content


def test_markdown_export_is_valid_markdown() -> None:
    """Test that exported file is valid Markdown."""
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Valid Test",
            project_root="/test",
        ),
        title="Valid Markdown Report",
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
        output_file = Path(temp_dir) / "valid.md"
        MarkdownExporter.export(report, output_file)

        content = output_file.read_text()
        # Check Markdown structure
        assert content.startswith("#")  # Should start with heading
        assert "##" in content  # Should have subheadings
        assert "|" in content  # Should have tables
        assert "-" in content or "*" in content  # Should have lists


def test_markdown_export_contains_metadata() -> None:
    """Test that Markdown export includes metadata."""
    project_name = "Metadata Test Project"
    author = "Jane Doe"
    
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name=project_name,
            project_root="/path/to/project",
            author=author,
        ),
        title="Metadata Report",
        report_type=ReportTypeEnum.SUMMARY,
        summary=KPISummary(
            total_keywords=25,
            unused_keywords=1,
            reusage_rate=78.0,
            documentation_coverage=92.0,
            robocop_issues=4,
            total_files=11,
        ),
        risk_level="LOW",
        health_status="Good project health.",
        robocop_issues_by_category={},
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "metadata.md"
        MarkdownExporter.export(report, output_file)

        content = output_file.read_text()
        assert project_name in content
        assert author in content
        assert "## Report Metadata" in content
        assert "RoboView" in content


def test_markdown_export_creates_directories() -> None:
    """Test that Markdown export creates necessary directories."""
    report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Dir Test",
            project_root="/test",
        ),
        title="Directory Test",
        report_type=ReportTypeEnum.SUMMARY,
        summary=KPISummary(
            total_keywords=15,
            unused_keywords=1,
            reusage_rate=80.0,
            documentation_coverage=90.0,
            robocop_issues=2,
            total_files=8,
        ),
        risk_level="OPTIMAL",
        health_status="Excellent project health.",
        robocop_issues_by_category={},
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        output_file = Path(temp_dir) / "reports" / "2024" / "report.md"
        MarkdownExporter.export(report, output_file)

        assert output_file.exists()
        assert output_file.parent.exists()
