"""Main CLI entry point for RoboView."""

from pathlib import Path

import typer
import uvicorn
from roboview.cli.reporting import app as reporting_app

app = typer.Typer(help="RoboView - Robot Framework Keyword Management Tool")

# Add sub-apps
app.add_typer(reporting_app, name="report", help="Report generation commands")


@app.command()
def version() -> None:
    """Show RoboView version."""
    typer.echo("RoboView v0.0.4")


@app.command()
def serve(
    host: str = typer.Option(
        "127.0.0.1",
        "--host",
        "-h",
        help="Host to bind the server to",
    ),
    port: int = typer.Option(
        18123,
        "--port",
        "-p",
        help="Port to run the server on",
    ),
    project_root: Path = typer.Option(
        ".",
        "--project",
        help="Project root directory to analyze",
    ),
    robocop_config: Path | None = typer.Option(
        None,
        "--robocop-config",
        help="Path to robocop configuration file",
    ),
    log_level: str = typer.Option(
        "info",
        "--log-level",
        help="Log level (debug, info, warning, error)",
    ),
) -> None:
    """Start the RoboView backend server for headless workflows.

    This command starts the FastAPI server that provides REST APIs for
    keyword analysis, file analysis, and report generation.

    Examples:
        # Start server with defaults
        roboview serve

        # Start server on custom port
        roboview serve --port 8080

        # Start server with specific project
        roboview serve --project /path/to/rf-project

        # Start with debug logging
        roboview serve --log-level debug
    """
    import os

    # Set environment variables for the server
    os.environ["PROJECT_ROOT"] = str(project_root.resolve())
    if robocop_config:
        os.environ["ROBOCOP_CONFIG"] = str(robocop_config.resolve())
    os.environ["LOG_LEVEL"] = log_level.upper()

    typer.echo(f"🚀 Starting RoboView server...")
    typer.echo(f"📁 Project: {project_root.resolve()}")
    typer.echo(f"🌐 URL: http://{host}:{port}")
    typer.echo(f"📋 API Docs: http://{host}:{port}/docs")
    typer.echo("")
    typer.echo("Press Ctrl+C to stop the server.")

    uvicorn.run(
        "roboview.main:app",
        host=host,
        port=port,
        log_level=log_level.lower(),
        reload=False,
    )


@app.command()
def analyze(
    project_root: Path = typer.Option(
        ".",
        "--project",
        "-p",
        help="Project root directory to analyze",
    ),
    output: Path = typer.Option(
        "roboview-report.html",
        "--output",
        "-o",
        help="Output HTML report file path",
    ),
    author: str | None = typer.Option(
        None,
        "--author",
        "-a",
        help="Author name for the report",
    ),
    robocop_config: Path | None = typer.Option(
        None,
        "--robocop-config",
        help="Path to robocop configuration file",
    ),
    quiet: bool = typer.Option(
        False,
        "--quiet",
        "-q",
        help="Suppress output except errors",
    ),
) -> None:
    """Analyze a Robot Framework project and generate a comprehensive HTML report.

    This command analyzes the project and generates a single comprehensive
    report suitable for all audiences (business analysts, developers, project owners).

    Examples:
        # Basic analysis with default settings
        roboview analyze --project ./my-rf-project

        # Specify output file
        roboview analyze --project . --output qa-report.html

        # Quiet mode for CI/CD pipelines
        roboview analyze --project . --output report.html --quiet

        # Full options
        roboview analyze \\
            --project ./rf-tests \\
            --output ./reports/analysis.html \\
            --author "CI Pipeline" \\
            --robocop-config ./robocop.toml
    """
    from roboview.services.file_register_service import FileRegistryService
    from roboview.services.keyword_register_service import KeywordRegistryService
    from roboview.services.keyword_similarity_service import KeywordSimilarityService
    from roboview.services.keyword_usage_service import KeywordUsageService
    from roboview.services.reporting_service import ReportingService
    from roboview.services.robocop_register_service import RobocopRegistryService
    from roboview.services.robocop_service import RobocopService
    from roboview.utils.exporters.html_exporter import HTMLExporter

    def log(message: str) -> None:
        if not quiet:
            typer.echo(message)

    try:
        log("🔍 Analyzing Robot Framework project...")
        log(f"📁 Project: {project_root.resolve()}")

        # Validate project root
        if not project_root.exists():
            typer.echo(f"❌ Error: Project directory does not exist: {project_root}", err=True)
            raise typer.Exit(code=1)

        # Initialize registries
        log("📊 Initializing registries...")
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
        log("🔧 Initializing analysis services...")
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
        log("📝 Generating summary report...")
        report = reporting_service.generate_report(author=author)

        # Ensure output path has .html extension
        output_path = Path(output)
        if output_path.suffix.lower() != ".html":
            output_path = Path(str(output_path) + ".html")

        # Create output directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Export report
        log("💾 Exporting HTML report...")
        HTMLExporter.export(report, output_path)

        file_size = output_path.stat().st_size
        size_str = f"{file_size / 1024:.1f} KB" if file_size > 1024 else f"{file_size} bytes"

        log("")
        log("✅ Analysis complete!")
        log(f"📄 Report: {output_path.resolve()}")
        log(f"🏢 Project: {report.metadata.project_name}")
        log(f"📏 Size: {size_str}")

        # Print summary metrics
        log("")
        log("📈 Key Metrics:")
        log(f"   • Total Keywords: {report.summary.total_keywords}")
        log(f"   • Unused Keywords: {report.summary.unused_keywords}")
        log(f"   • Reusage Rate: {report.summary.reusage_rate:.1f}%")
        log(f"   • Documentation Coverage: {report.summary.documentation_coverage:.1f}%")
        log(f"   • Robocop Issues: {report.summary.robocop_issues}")
        log(f"   • Total Files: {report.summary.total_files}")
        log(f"   • Quality Score: {report.quality_scores.overall_score:.1f}/100")
        log(f"   • Risk Level: {report.risk_level}")

    except typer.Exit:
        raise
    except Exception as e:
        typer.echo(f"❌ Error: {e}", err=True)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
