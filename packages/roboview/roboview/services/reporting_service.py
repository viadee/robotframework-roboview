"""Service class implementing the reporting functionality."""

import logging
from pathlib import Path

from roboview.registries.file_registry import FileRegistry
from roboview.registries.keyword_registry import KeywordRegistry
from roboview.registries.robocop_registry import RobocopRegistry
from roboview.schemas.domain.reports import (
    DuplicateKeywordPair,
    FileReportData,
    KeywordReportData,
    KPISummary,
    Recommendation,
    ReportMetadata,
    ReportTypeEnum,
    RobocopIssueData,
    SummaryReport,
)
from roboview.services.keyword_similarity_service import KeywordSimilarityService
from roboview.services.keyword_usage_service import KeywordUsageService
from roboview.services.robocop_service import RobocopService
from roboview.utils.directory_parsing import DirectoryParser

logger = logging.getLogger(__name__)

# Quality threshold constants
_DOCUMENTATION_COVERAGE_HIGH = 70
_DOCUMENTATION_COVERAGE_LOW = 50
_UNUSED_KEYWORDS_RATIO_THRESHOLD = 0.1
_REUSAGE_RATE_THRESHOLD = 60
_ISSUE_DENSITY_THRESHOLD = 0.5
_ROBOCOP_ISSUES_THRESHOLD = 20
_SIMILARITY_SCORE_THRESHOLD = 70

# Risk level score thresholds
_SCORE_OPTIMAL = 81
_SCORE_LOW = 61
_SCORE_MEDIUM = 41
_SCORE_HIGH = 21


class ReportingService:
    """Service class to provide reporting functionality."""

    def __init__(  # noqa: PLR0913
        self,
        keyword_registry: KeywordRegistry,
        file_registry: FileRegistry,
        robocop_registry: RobocopRegistry,
        keyword_usage_service: KeywordUsageService,
        keyword_similarity_service: KeywordSimilarityService,
        robocop_service: RobocopService,
        project_root: Path,
    ) -> None:
        """Initialize ReportingService.

        Arguments:
            keyword_registry: Initialized keyword registry object.
            file_registry: Initialized file registry object.
            robocop_registry: Initialized robocop registry object.
            keyword_usage_service: Initialized keyword usage service.
            keyword_similarity_service: Initialized keyword similarity service.
            robocop_service: Initialized robocop service.
            project_root: Root path of the project.

        """
        self.keyword_registry = keyword_registry
        self.file_registry = file_registry
        self.robocop_registry = robocop_registry
        self.keyword_usage_service = keyword_usage_service
        self.keyword_similarity_service = keyword_similarity_service
        self.robocop_service = robocop_service
        self.project_root = project_root

    def _get_project_name(self) -> str:
        """Get project name from root path."""
        return self.project_root.name or "Robot Framework Project"

    def _build_kpi_summary(self) -> KPISummary:
        """Build KPI summary from registries and services."""
        keyword_reusage_rate = self.keyword_usage_service.get_keyword_reusage_rate()
        documentation_coverage = self.keyword_usage_service.get_documentation_coverage()
        num_user_keywords = len(self.keyword_registry.get_user_defined_keywords())
        num_unused_keywords = len(self.keyword_usage_service.get_keywords_without_usages())
        num_robocop_issues = len(self.robocop_service.get_robocop_error_messages())

        directory_parser = DirectoryParser(self.project_root)
        robot_files = directory_parser.get_test_file_paths()
        resource_files = directory_parser.get_resource_file_paths()
        num_parsed_files = len(robot_files) + len(resource_files)

        return KPISummary(
            total_keywords=num_user_keywords,
            unused_keywords=num_unused_keywords,
            reusage_rate=keyword_reusage_rate,
            documentation_coverage=documentation_coverage,
            robocop_issues=num_robocop_issues,
            total_files=num_parsed_files,
        )

    def _calculate_overall_score(self, kpi_summary: KPISummary) -> float:
        """Calculate overall health score from KPI summary.

        The score is a weighted average of:
        - Reusage rate (25%)
        - Documentation coverage (25%)
        - Reliability (25%) - inverse of issue density
        - Technical debt (25%) - inverse of unused keyword ratio

        """
        # Reliability: inverse of issue density
        if kpi_summary.total_keywords > 0:
            issue_density = (kpi_summary.robocop_issues / kpi_summary.total_keywords) * 100
            reliability = max(0, 100 - issue_density)
        else:
            reliability = 100

        # Technical debt: inverse of unused keyword ratio
        if kpi_summary.total_keywords > 0:
            debt_ratio = (kpi_summary.unused_keywords / kpi_summary.total_keywords) * 100
            technical_debt = max(0, 100 - debt_ratio)
        else:
            technical_debt = 100

        return (
            (kpi_summary.reusage_rate * 0.25)
            + (kpi_summary.documentation_coverage * 0.25)
            + (reliability * 0.25)
            + (technical_debt * 0.25)
        )

    def _build_recommendations(self, kpi_summary: KPISummary) -> list[Recommendation]:
        """Build recommendations based on metrics."""
        recommendations = []

        # Documentation recommendations
        if kpi_summary.documentation_coverage < _DOCUMENTATION_COVERAGE_HIGH:
            keywords_without_docs = self.keyword_usage_service.get_keywords_without_documentation()
            recommendations.append(
                Recommendation(
                    priority="HIGH",
                    category="Documentation",
                    message=f"Add documentation to {len(keywords_without_docs)} keywords",
                    affected_items=[kw.keyword_name_without_prefix for kw in keywords_without_docs[:5]],
                )
            )

        # Unused keywords recommendations
        unused_ratio = kpi_summary.unused_keywords / kpi_summary.total_keywords
        if kpi_summary.unused_keywords > 0 and unused_ratio > _UNUSED_KEYWORDS_RATIO_THRESHOLD:
            unused = self.keyword_usage_service.get_keywords_without_usages()
            recommendations.append(
                Recommendation(
                    priority="MEDIUM",
                    category="Dead Code",
                    message=f"Remove or refactor {len(unused)} unused keywords",
                    affected_items=[kw.keyword_name_without_prefix for kw in unused[:5]],
                )
            )

        # Reusability recommendations
        if kpi_summary.reusage_rate < _REUSAGE_RATE_THRESHOLD:
            recommendations.append(
                Recommendation(
                    priority="MEDIUM",
                    category="Code Reusability",
                    message="Improve keyword reusability by creating more abstract, reusable keywords",
                    details="Consider extracting common patterns into shared keywords",
                )
            )

        # Code quality recommendations
        if kpi_summary.robocop_issues > 0:
            issue_density = kpi_summary.robocop_issues / max(1, kpi_summary.total_keywords)
            if issue_density > _ISSUE_DENSITY_THRESHOLD:
                recommendations.append(
                    Recommendation(
                        priority="HIGH",
                        category="Code Quality",
                        message=f"Address {kpi_summary.robocop_issues} code quality issues",
                        details="Run robocop to see detailed violations",
                    )
                )

        return recommendations

    def _get_risk_level(self, kpi_summary: KPISummary) -> str:
        """Determine risk level based on overall score."""
        score = self._calculate_overall_score(kpi_summary)
        if score >= _SCORE_OPTIMAL:
            return "OPTIMAL"
        if score >= _SCORE_LOW:
            return "LOW"
        if score >= _SCORE_MEDIUM:
            return "MEDIUM"
        if score >= _SCORE_HIGH:
            return "HIGH"
        return "CRITICAL"

    def _get_health_status(self, kpi_summary: KPISummary) -> str:
        """Generate a human-readable health status summary."""
        score = self._calculate_overall_score(kpi_summary)
        issues = []

        if kpi_summary.unused_keywords > 0:
            issues.append(f"{kpi_summary.unused_keywords} unused keywords")
        if kpi_summary.documentation_coverage < _DOCUMENTATION_COVERAGE_LOW:
            issues.append("low documentation coverage")
        if kpi_summary.robocop_issues > _ROBOCOP_ISSUES_THRESHOLD:
            issues.append(f"{kpi_summary.robocop_issues} code quality issues")

        if score >= _SCORE_OPTIMAL:
            status = "Excellent project health."
        elif score >= _SCORE_LOW:
            status = "Good project health with minor improvements needed."
        elif score >= _SCORE_MEDIUM:
            status = "Moderate project health requiring attention."
        elif score >= _SCORE_HIGH:
            status = "Poor project health with significant issues."
        else:
            status = "Critical project health requiring immediate action."

        if issues:
            status += f" Key concerns: {', '.join(issues)}."

        return status

    def generate_summary_report(self, author: str | None = None) -> SummaryReport:
        """Generate a comprehensive summary report.

        This report combines executive overview, technical details, and quality
        assessment into a single comprehensive document suitable for all audiences.

        Arguments:
            author: Optional author name

        Returns:
            SummaryReport: The generated comprehensive summary report

        """
        try:
            metadata = ReportMetadata(
                project_name=self._get_project_name(),
                project_root=str(self.project_root),
                author=author,
            )
            title = f"RoboView Summary Report - {metadata.project_name}"

            # Build core metrics
            kpi_summary = self._build_kpi_summary()
            recommendations = self._build_recommendations(kpi_summary)
            risk_level = self._get_risk_level(kpi_summary)
            health_status = self._get_health_status(kpi_summary)

            # Get robocop issues
            robocop_issues = self.robocop_service.get_robocop_error_messages()
            issues_data = [
                RobocopIssueData(
                    issue_id=issue.message_id,
                    file_path=issue.source,
                    line_number=None,  # RobocopMessage doesn't track line numbers separately
                    severity=issue.severity,
                    category=str(issue.category) if issue.category else "Unknown",
                    message=issue.message,
                )
                for issue in robocop_issues
            ]

            # Group robocop issues
            by_category: dict[str, int] = {}
            by_severity: dict[str, int] = {}
            file_issue_count: dict[str, int] = {}

            for issue in robocop_issues:
                category = str(issue.category) if issue.category else "Unknown"
                severity = issue.severity or "INFO"
                by_category[category] = by_category.get(category, 0) + 1
                by_severity[severity] = by_severity.get(severity, 0) + 1
                file_issue_count[issue.source] = file_issue_count.get(issue.source, 0) + 1

            # Identify risk files (top 10 with most issues)
            sorted_risk = sorted(file_issue_count.items(), key=lambda x: x[1], reverse=True)
            risk_files = [file_path for file_path, _ in sorted_risk[:10]]

            # Get most used keywords (top 10)
            most_used = self.keyword_usage_service.get_most_used_user_defined_keywords(10)
            most_used_data = [
                KeywordReportData(
                    keyword_id=ku.keyword_id,
                    keyword_name=ku.keyword_name_without_prefix,
                    file_name=ku.file_name,
                    line_number=ku.line_number,
                    documentation=ku.documentation,
                    usage_count=ku.total_usages,
                    is_user_defined=True,
                    source=ku.source,
                )
                for ku in most_used
            ]

            # Get unused keywords
            unused = self.keyword_usage_service.get_keywords_without_usages()
            unused_data = [
                KeywordReportData(
                    keyword_id=ku.keyword_id,
                    keyword_name=ku.keyword_name_without_prefix,
                    file_name=ku.file_name,
                    line_number=ku.line_number,
                    documentation=ku.documentation,
                    usage_count=0,
                    is_user_defined=True,
                    source=ku.source,
                )
                for ku in unused
            ]

            # Get undocumented keywords
            undocumented = self.keyword_usage_service.get_keywords_without_documentation()
            undocumented_data = [
                KeywordReportData(
                    keyword_id=ku.keyword_id,
                    keyword_name=ku.keyword_name_without_prefix,
                    file_name=ku.file_name,
                    line_number=ku.line_number,
                    documentation=ku.documentation,
                    usage_count=ku.total_usages,
                    is_user_defined=True,
                    source=ku.source,
                )
                for ku in undocumented
            ]

            # Get duplicate/similar keywords
            duplicates = []
            # Get keywords that have high similarity with others
            keywords_with_similarity = self.keyword_similarity_service.get_all_similar_keywords_above_threshold()
            seen_pairs: set[tuple[str, str]] = set()
            for kw in keywords_with_similarity:
                if kw is None:
                    continue
                kw_name = kw.keyword_name_without_prefix
                # Get similar keywords for this keyword
                similar_list = self.keyword_similarity_service.get_n_most_similar_keywords(kw_name, 10)
                for similar_kw in similar_list:
                    if similar_kw.score >= _SIMILARITY_SCORE_THRESHOLD:
                        # Avoid duplicate pairs
                        sorted_names = sorted([kw_name, similar_kw.keyword_name_without_prefix])
                        pair_key: tuple[str, str] = (sorted_names[0], sorted_names[1])
                        if pair_key not in seen_pairs:
                            seen_pairs.add(pair_key)
                            duplicates.append(
                                DuplicateKeywordPair(
                                    keyword1_name=kw_name,
                                    keyword1_file=kw.source,
                                    keyword2_name=similar_kw.keyword_name_without_prefix,
                                    keyword2_file=similar_kw.source,
                                    similarity_score=similar_kw.score,
                                )
                            )

            # Collect file data
            files_data = [
                FileReportData(
                    file_name=file_obj.file_name,
                    file_path=file_obj.path,
                    is_resource=file_obj.is_resource,
                    keywords_defined=len(file_obj.initialized_keywords or []),
                    keywords_called=len(file_obj.called_keywords or []),
                    total_lines=0,
                )
                for file_obj in self.file_registry.get_all_files()
            ]

            # Calculate best practices score from KPI metrics
            # Reliability: inverse of issue density
            if kpi_summary.total_keywords > 0:
                issue_density = (kpi_summary.robocop_issues / kpi_summary.total_keywords) * 100
                reliability = max(0, 100 - issue_density)
            else:
                reliability = 100

            best_practices_score = (
                kpi_summary.documentation_coverage * 0.4
                + reliability * 0.4
                + (100 - min(50, (len(risk_files) / max(1, kpi_summary.total_files)) * 100)) * 0.2
            )

            return SummaryReport(
                metadata=metadata,
                title=title,
                report_type=ReportTypeEnum.SUMMARY,
                summary=kpi_summary,
                recommendations=recommendations,
                risk_level=risk_level,
                health_status=health_status,
                most_used_keywords=most_used_data,
                unused_keywords=unused_data,
                undocumented_keywords=undocumented_data,
                duplicate_keywords=duplicates,
                files=files_data,
                risk_files=risk_files,
                robocop_issues=issues_data,
                robocop_issues_by_category=by_category,
                robocop_issues_by_severity=by_severity,
                best_practices_score=best_practices_score,
            )

        except Exception:
            logger.exception("Error generating summary report")
            raise

    def generate_report(self, author: str | None = None) -> SummaryReport:
        """Generate a comprehensive summary report.

        Arguments:
            author: Optional author name

        Returns:
            SummaryReport: The generated report

        """
        return self.generate_summary_report(author)
