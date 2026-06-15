"""CLI commands for report generation."""

import logging
from pathlib import Path
from typing import Annotated

import typer
from roboview.services.file_register_service import FileRegistryService
from roboview.services.keyword_register_service import KeywordRegistryService
from roboview.services.keyword_similarity_service import KeywordSimilarityService
from roboview.services.keyword_usage_service import KeywordUsageService
from roboview.services.reporting_service import ReportingService
from roboview.services.robocop_register_service import RobocopRegistryService
from roboview.services.robocop_service import RobocopService
from roboview.utils.exporters.html_exporter import HTMLExporter

logger = logging.getLogger(__name__)

app = typer.Typer(help="RoboView reporting commands")

# Constants
_KB = 1024


@app.command()
def generate(
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output file path (HTML format)"),
    ] = Path("roboview-report.html"),
    project_root: Annotated[
        Path,
        typer.Option("--project", "-p", help="Project root directory"),
    ] = Path(),
    author: Annotated[
        str | None,
        typer.Option("--author", "-a", help="Author of the report"),
    ] = None,
    robocop_config: Annotated[
        Path | None,
        typer.Option("--robocop-config", help="Path to robocop configuration file"),
    ] = None,
) -> None:
    """Generate a comprehensive HTML summary report for a Robot Framework project.

    The report includes:
    - Executive overview with risk level and health status
    - Key performance indicators (KPIs)
    - Quality scores and recommendations
    - Keyword analysis (most used, unused, undocumented, duplicates)
    - File analysis
    - Code quality issues (Robocop)

    Examples:
        # Generate report with defaults
        roboview report generate --project .

        # Specify output file
        roboview report generate --output analysis.html --project ./rf-tests

        # With author
        roboview report generate --author "QA Team" --output report.html

    """
    try:
        typer.echo("🚀 Generating summary report...")
        typer.echo(f"📁 Project: {project_root}")
        typer.echo(f"💾 Output: {output}")

        # Initialize registries
        typer.echo("📊 Initializing registries...")
        keyword_registry_service = KeywordRegistryService(project_root)
        keyword_registry_service.initialize()
        keyword_registry = keyword_registry_service.get_keyword_registry()

        file_registry_service = FileRegistryService(project_root)
        file_registry_service.initialize()
        file_registry = file_registry_service.get_file_registry()

        robocop_registry_service = RobocopRegistryService(
            project_root,
            robocop_config,
        )
        robocop_registry_service.initialize()
        robocop_registry = robocop_registry_service.get_robocop_registry()

        # Initialize services
        typer.echo("🔧 Initializing services...")
        keyword_usage_service = KeywordUsageService(keyword_registry, file_registry)

        keyword_similarity_service = KeywordSimilarityService(keyword_registry)
        keyword_similarity_service.calculate_keyword_similarity_matrix()

        robocop_service = RobocopService(robocop_registry)

        reporting_service = ReportingService(
            keyword_registry,
            file_registry,
            robocop_registry,
            keyword_usage_service,
            keyword_similarity_service,
            robocop_service,
            project_root,
        )

        # Generate report
        typer.echo("📝 Generating report...")
        report = reporting_service.generate_report(author=author)

        # Ensure output path has .html extension
        output_path = Path(output)
        if output_path.suffix.lower() != ".html":
            output_path = Path(str(output_path) + ".html")

        # Export report as HTML
        typer.echo("💾 Exporting report as HTML...")
        HTMLExporter.export(report, output_path)

        file_size = output_path.stat().st_size
        size_str = f"{file_size / _KB:.1f} KB" if file_size > _KB else f"{file_size} bytes"

        typer.echo("")
        typer.echo("✅ Report generated successfully!")
        typer.echo(f"📄 File: {output_path.resolve()}")
        typer.echo(f"🏢 Project: {report.metadata.project_name}")
        typer.echo(f"📏 File Size: {size_str}")
        typer.echo(f"⚡ Risk Level: {report.risk_level}")
        typer.echo(f"📊 Best Practices Score: {report.best_practices_score:.1f}/100")

    except Exception:
        logger.exception("Error generating report")
        typer.echo("❌ Error generating report", err=True)
        raise typer.Exit(code=1) from None


@app.command()
def version() -> None:
    """Show version information."""
    typer.echo("RoboView Reporting CLI v0.0.4")


if __name__ == "__main__":
    app()
