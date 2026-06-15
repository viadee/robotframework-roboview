"""Tests for the reporting service."""

from pathlib import Path
from unittest.mock import MagicMock

from roboview.registries.file_registry import FileRegistry
from roboview.registries.keyword_registry import KeywordRegistry
from roboview.registries.robocop_registry import RobocopRegistry
from roboview.schemas.domain.reports import ReportTypeEnum
from roboview.services.keyword_similarity_service import KeywordSimilarityService
from roboview.services.keyword_usage_service import KeywordUsageService
from roboview.services.reporting_service import ReportingService
from roboview.services.robocop_service import RobocopService


def test_reporting_service_initialization():
    """Test that ReportingService initializes correctly."""
    # Create mock dependencies
    keyword_registry = MagicMock(spec=KeywordRegistry)
    file_registry = MagicMock(spec=FileRegistry)
    robocop_registry = MagicMock(spec=RobocopRegistry)
    keyword_usage_service = MagicMock(spec=KeywordUsageService)
    keyword_similarity_service = MagicMock(spec=KeywordSimilarityService)
    robocop_service = MagicMock(spec=RobocopService)
    project_root = Path("/test/project")

    # Create reporting service
    service = ReportingService(
        keyword_registry=keyword_registry,
        file_registry=file_registry,
        robocop_registry=robocop_registry,
        keyword_usage_service=keyword_usage_service,
        keyword_similarity_service=keyword_similarity_service,
        robocop_service=robocop_service,
        project_root=project_root,
    )

    # Verify initialization
    assert service.keyword_registry == keyword_registry
    assert service.file_registry == file_registry
    assert service.robocop_registry == robocop_registry
    assert service.keyword_usage_service == keyword_usage_service
    assert service.keyword_similarity_service == keyword_similarity_service
    assert service.robocop_service == robocop_service
    assert service.project_root == project_root


def test_generate_executive_summary_report():
    """Test generating an executive summary report."""
    # Create mock dependencies with return values
    keyword_registry = MagicMock(spec=KeywordRegistry)
    keyword_registry.get_user_defined_keywords.return_value = [MagicMock()] * 42

    file_registry = MagicMock(spec=FileRegistry)
    robocop_registry = MagicMock(spec=RobocopRegistry)

    keyword_usage_service = MagicMock(spec=KeywordUsageService)
    keyword_usage_service.get_keyword_reusage_rate.return_value = 65.5
    keyword_usage_service.get_documentation_coverage.return_value = 80.0
    keyword_usage_service.get_keywords_without_usages.return_value = []

    keyword_similarity_service = MagicMock(spec=KeywordSimilarityService)

    robocop_service = MagicMock(spec=RobocopService)
    robocop_service.get_robocop_error_messages.return_value = []

    project_root = Path("/test/project")

    service = ReportingService(
        keyword_registry=keyword_registry,
        file_registry=file_registry,
        robocop_registry=robocop_registry,
        keyword_usage_service=keyword_usage_service,
        keyword_similarity_service=keyword_similarity_service,
        robocop_service=robocop_service,
        project_root=project_root,
    )

    # Generate report
    report = service.generate_executive_summary_report(author="Test Author")

    # Verify report
    assert report.report_type == ReportTypeEnum.EXECUTIVE_SUMMARY
    assert report.metadata.project_name == "project"
    assert report.metadata.author == "Test Author"
    assert report.summary.total_keywords == 42
    assert report.summary.reusage_rate == 65.5
    assert report.summary.documentation_coverage == 80.0
    assert report.quality_scores is not None
    assert 0 <= report.quality_scores.overall_score <= 100


def test_quality_score_calculation():
    """Test quality score calculation."""
    keyword_registry = MagicMock(spec=KeywordRegistry)
    keyword_registry.get_user_defined_keywords.return_value = [MagicMock()] * 50

    file_registry = MagicMock(spec=FileRegistry)
    robocop_registry = MagicMock(spec=RobocopRegistry)

    keyword_usage_service = MagicMock(spec=KeywordUsageService)
    keyword_usage_service.get_keyword_reusage_rate.return_value = 80.0
    keyword_usage_service.get_documentation_coverage.return_value = 90.0
    keyword_usage_service.get_keywords_without_usages.return_value = []

    keyword_similarity_service = MagicMock(spec=KeywordSimilarityService)

    robocop_service = MagicMock(spec=RobocopService)
    robocop_service.get_robocop_error_messages.return_value = [MagicMock()] * 5

    project_root = Path("/test/project")

    service = ReportingService(
        keyword_registry=keyword_registry,
        file_registry=file_registry,
        robocop_registry=robocop_registry,
        keyword_usage_service=keyword_usage_service,
        keyword_similarity_service=keyword_similarity_service,
        robocop_service=robocop_service,
        project_root=project_root,
    )

    report = service.generate_executive_summary_report()

    # Quality score should be positive and reasonable
    assert report.quality_scores.overall_score > 60
    assert report.quality_scores.reusability_index == 80.0
    assert report.quality_scores.maintainability_index == 90.0


def test_risk_level_determination():
    """Test risk level determination based on quality score."""
    keyword_registry = MagicMock(spec=KeywordRegistry)
    keyword_registry.get_user_defined_keywords.return_value = []

    file_registry = MagicMock(spec=FileRegistry)
    robocop_registry = MagicMock(spec=RobocopRegistry)

    keyword_usage_service = MagicMock(spec=KeywordUsageService)
    keyword_usage_service.get_keyword_reusage_rate.return_value = 50.0
    keyword_usage_service.get_documentation_coverage.return_value = 50.0
    keyword_usage_service.get_keywords_without_usages.return_value = []

    keyword_similarity_service = MagicMock(spec=KeywordSimilarityService)

    robocop_service = MagicMock(spec=RobocopService)
    robocop_service.get_robocop_error_messages.return_value = []

    project_root = Path("/test/project")

    service = ReportingService(
        keyword_registry=keyword_registry,
        file_registry=file_registry,
        robocop_registry=robocop_registry,
        keyword_usage_service=keyword_usage_service,
        keyword_similarity_service=keyword_similarity_service,
        robocop_service=robocop_service,
        project_root=project_root,
    )

    report = service.generate_executive_summary_report()

    # Risk level should be determined
    assert report.risk_level in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "OPTIMAL"]
    assert report.risk_level in ["MEDIUM", "LOW", "OPTIMAL"]  # Score should be around 50
