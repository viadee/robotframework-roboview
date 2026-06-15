---
name: report-generation
description: Report generation feature development for RoboView. Use when working on the reporting service, exporters, or report-related endpoints. Covers PDF, HTML, Excel, JSON, and Markdown export formats.
applyTo: "packages/roboview/roboview/**/report*.py,packages/roboview/roboview/utils/exporters/**/*.py"
---

# RoboView Report Generation Development

## Architecture Overview

The reporting system generates quality analysis reports in multiple formats from RoboView's analysis data.

```
packages/roboview/roboview/
├── services/
│   └── reporting_service.py    # Main report generation service
├── schemas/domain/
│   └── reports.py              # Report data models
└── utils/exporters/
    ├── __init__.py
    ├── pdf_exporter.py         # ReportLab-based PDF export
    ├── html_exporter.py        # HTML template export
    ├── excel_exporter.py       # OpenPyXL-based Excel export
    ├── json_exporter.py        # JSON export
    └── markdown_exporter.py    # Markdown export
```

## Report Data Model

```python
# schemas/domain/reports.py
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ReportFormat(str, Enum):
    PDF = "pdf"
    HTML = "html"
    EXCEL = "excel"
    JSON = "json"
    MARKDOWN = "markdown"

class KPISummary(BaseModel):
    """Key performance indicators for the report."""
    
    total_keywords: int = Field(description="Total user-defined keywords")
    unused_keywords: int = Field(description="Keywords with no usages")
    documentation_coverage: float = Field(description="Percentage with [Documentation]")
    reusage_rate: float = Field(description="Percentage used more than once")
    robocop_issues: int = Field(description="Total Robocop issues")
    total_files: int = Field(description="Total Robot Framework files")

class Recommendation(BaseModel):
    """Improvement recommendation."""
    
    category: str
    priority: str  # High, Medium, Low
    title: str
    description: str
    affected_files: list[str] = Field(default_factory=list)

class Report(BaseModel):
    """Complete analysis report."""
    
    metadata: ReportMetadata
    kpi_summary: KPISummary
    recommendations: list[Recommendation]
    detailed_findings: dict  # Flexible for different report sections
```

## ReportingService Implementation

```python
# services/reporting_service.py
from roboview.registries import KeywordRegistry, FileRegistry, RobocopRegistry
from roboview.services import KeywordUsageService, RobocopService
from roboview.schemas.domain.reports import Report, ReportFormat
from roboview.utils.exporters import (
    PDFExporter,
    HTMLExporter,
    ExcelExporter,
    JSONExporter,
    MarkdownExporter,
)

class ReportingService:
    """Service for generating analysis reports."""
    
    def __init__(
        self,
        keyword_registry: KeywordRegistry,
        file_registry: FileRegistry,
        robocop_registry: RobocopRegistry,
        keyword_usage_service: KeywordUsageService,
        robocop_service: RobocopService,
    ) -> None:
        self._keyword_registry = keyword_registry
        self._file_registry = file_registry
        self._robocop_registry = robocop_registry
        self._keyword_usage_service = keyword_usage_service
        self._robocop_service = robocop_service
        
        self._exporters = {
            ReportFormat.PDF: PDFExporter(),
            ReportFormat.HTML: HTMLExporter(),
            ReportFormat.EXCEL: ExcelExporter(),
            ReportFormat.JSON: JSONExporter(),
            ReportFormat.MARKDOWN: MarkdownExporter(),
        }
    
    def generate_report(
        self,
        format: ReportFormat,
        output_path: str,
        project_name: str | None = None,
    ) -> str:
        """
        Generate a report in the specified format.
        
        Args:
            format: Output format (PDF, HTML, Excel, JSON, Markdown).
            output_path: Path to write the report.
            project_name: Optional project name for the report header.
            
        Returns:
            Path to the generated report file.
        """
        report = self._build_report(project_name)
        exporter = self._exporters[format]
        return exporter.export(report, output_path)
    
    def _build_report(self, project_name: str | None) -> Report:
        """Build report from current analysis data."""
        return Report(
            metadata=self._build_metadata(project_name),
            kpi_summary=self._build_kpi_summary(),
            recommendations=self._build_recommendations(),
            detailed_findings=self._build_detailed_findings(),
        )
    
    def _build_kpi_summary(self) -> KPISummary:
        """Build KPI summary from services."""
        keywords = self._keyword_registry.get_user_defined_keywords()
        unused = self._keyword_usage_service.get_keywords_without_usages()
        doc_coverage = self._keyword_usage_service.get_documentation_coverage()
        reusage_rate = self._keyword_usage_service.get_keyword_reusage_rate()
        robocop_issues = len(self._robocop_registry.get_all_error_messages())
        files = self._file_registry.get_all_files()
        
        return KPISummary(
            total_keywords=len(keywords),
            unused_keywords=len(unused),
            documentation_coverage=doc_coverage,
            reusage_rate=reusage_rate,
            robocop_issues=robocop_issues,
            total_files=len(files),
        )
    
    def _build_recommendations(self) -> list[Recommendation]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Check documentation
        undocumented = self._keyword_usage_service.get_keywords_without_documentation()
        if undocumented:
            recommendations.append(Recommendation(
                category="Documentation",
                priority="High" if len(undocumented) > 10 else "Medium",
                title="Add keyword documentation",
                description=f"{len(undocumented)} keywords lack [Documentation]",
                affected_files=list(set(k.file_name for k in undocumented[:10])),
            ))
        
        # Check unused keywords
        unused = self._keyword_usage_service.get_keywords_without_usages()
        if unused:
            recommendations.append(Recommendation(
                category="Maintenance",
                priority="Medium",
                title="Review unused keywords",
                description=f"{len(unused)} keywords are never called",
                affected_files=list(set(k.file_name for k in unused[:10])),
            ))
        
        return recommendations
```

## Exporter Implementation

### Base Exporter Pattern

```python
# utils/exporters/base.py
from abc import ABC, abstractmethod
from roboview.schemas.domain.reports import Report

class BaseExporter(ABC):
    """Base class for report exporters."""
    
    @abstractmethod
    def export(self, report: Report, output_path: str) -> str:
        """
        Export report to file.
        
        Args:
            report: Report data to export.
            output_path: Path to write the report.
            
        Returns:
            Absolute path to the generated file.
        """
        pass
    
    def _ensure_directory(self, path: str) -> None:
        """Ensure output directory exists."""
        from pathlib import Path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
```

### PDF Exporter

```python
# utils/exporters/pdf_exporter.py
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

class PDFExporter(BaseExporter):
    """Export reports to PDF format."""
    
    def export(self, report: Report, output_path: str) -> str:
        self._ensure_directory(output_path)
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        elements.append(Paragraph(
            f"RoboView Analysis Report: {report.metadata.project_name}",
            styles['Heading1']
        ))
        elements.append(Spacer(1, 20))
        
        # KPI Summary Table
        elements.append(Paragraph("Key Metrics", styles['Heading2']))
        kpi_data = [
            ["Metric", "Value"],
            ["Total Keywords", str(report.kpi_summary.total_keywords)],
            ["Unused Keywords", str(report.kpi_summary.unused_keywords)],
            ["Documentation Coverage", f"{report.kpi_summary.documentation_coverage:.1f}%"],
        ]
        kpi_table = Table(kpi_data)
        elements.append(kpi_table)
        
        # ... more sections
        
        doc.build(elements)
        return output_path
```

### HTML Exporter

```python
# utils/exporters/html_exporter.py
class HTMLExporter(BaseExporter):
    """Export reports to HTML format."""
    
    def export(self, report: Report, output_path: str) -> str:
        self._ensure_directory(output_path)
        
        html = self._render_template(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path
    
    def _render_template(self, report: Report) -> str:
        """Render report to HTML string."""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>RoboView Report - {report.metadata.project_name}</title>
    <style>
        body {{ font-family: system-ui, sans-serif; margin: 40px; }}
        .metric {{ display: inline-block; padding: 20px; margin: 10px; background: #f5f5f5; border-radius: 8px; }}
        .metric-value {{ font-size: 2em; font-weight: bold; }}
        .recommendation {{ padding: 15px; margin: 10px 0; border-left: 4px solid #007acc; background: #f0f7ff; }}
    </style>
</head>
<body>
    <h1>RoboView Analysis Report</h1>
    <h2>{report.metadata.project_name}</h2>
    <p>Generated: {report.metadata.generated_at}</p>
    
    <h3>Key Metrics</h3>
    <div class="metrics-grid">
        <div class="metric">
            <div class="metric-value">{report.kpi_summary.total_keywords}</div>
            <div>Total Keywords</div>
        </div>
        <!-- ... more metrics -->
    </div>
    
    <h3>Recommendations</h3>
    {"".join(self._render_recommendation(r) for r in report.recommendations)}
</body>
</html>
"""
```

## CLI Integration

```python
# cli/report.py
import typer
from roboview.schemas.domain.reports import ReportFormat

app = typer.Typer()

@app.command()
def generate(
    project_path: str = typer.Argument(..., help="Path to Robot Framework project"),
    output: str = typer.Option("./report", "-o", help="Output path"),
    format: ReportFormat = typer.Option(ReportFormat.HTML, "-f", help="Output format"),
    project_name: str | None = typer.Option(None, "--name", help="Project name"),
):
    """Generate an analysis report for a Robot Framework project."""
    from roboview.services import ReportingService
    
    # Initialize services...
    service = ReportingService(...)
    
    output_file = service.generate_report(format, output, project_name)
    typer.echo(f"Report generated: {output_file}")
```

## Testing Reports

```python
# tests/utest/services_tests/test_reporting_service.py
import pytest
from roboview.services import ReportingService
from roboview.schemas.domain.reports import ReportFormat

def test_generate_report_creates_html_file(tmp_path, initialized_registries):
    kw_registry, file_registry, robocop_registry = initialized_registries
    service = ReportingService(kw_registry, file_registry, robocop_registry, ...)
    
    output_path = tmp_path / "report.html"
    result = service.generate_report(ReportFormat.HTML, str(output_path))
    
    assert output_path.exists()
    assert "RoboView" in output_path.read_text()

def test_kpi_summary_calculates_correct_values(service_with_test_data):
    report = service_with_test_data._build_report("Test Project")
    
    assert report.kpi_summary.total_keywords == 5
    assert report.kpi_summary.unused_keywords == 1
    assert report.kpi_summary.documentation_coverage == 80.0
```
