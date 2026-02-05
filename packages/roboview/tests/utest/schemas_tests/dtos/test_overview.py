from roboview.schemas.domain.keywords import KeywordUsage
from roboview.schemas.domain.robocop import IssueSummary, RuleCategory
from roboview.schemas.dtos.overview import (
    KPIResponse,
    MostUsedKeywordsResponse,
    RobocopIssueSummaryResponse,
)


def _kw_usage(
        keyword_id: str,
        file_name: str,
        name_no_prefix: str,
        name_with_prefix: str,
        source: str,
        file_usages: int,
        total_usages: int,
        documentation: str | None = None,
) -> KeywordUsage:
    return KeywordUsage(
        keyword_id=keyword_id,
        file_name=file_name,
        keyword_name_without_prefix=name_no_prefix,
        keyword_name_with_prefix=name_with_prefix,
        documentation=documentation,
        source=source,
        file_usages=file_usages,
        total_usages=total_usages,
    )


def _issue_summary(category, count: int) -> IssueSummary:
    return IssueSummary(category=category, count=count)


def test_kpi_response_defaults():
    kpi = KPIResponse()

    assert kpi.num_user_keywords == 0
    assert kpi.num_unused_keywords == 0
    assert kpi.keyword_reusage_rate == 0.0
    assert kpi.num_robocop_issues == 0
    assert kpi.documentation_coverage == 0.0
    assert kpi.num_rf_files == 0


def test_kpi_response_custom_values():
    kpi = KPIResponse(
        num_user_keywords=10,
        num_unused_keywords=3,
        keyword_reusage_rate=0.75,
        num_robocop_issues=42,
        documentation_coverage=0.9,
        num_rf_files=7,
    )

    assert kpi.num_user_keywords == 10
    assert kpi.num_unused_keywords == 3
    assert kpi.keyword_reusage_rate == 0.75
    assert kpi.num_robocop_issues == 42
    assert kpi.documentation_coverage == 0.9
    assert kpi.num_rf_files == 7


def test_most_used_keywords_response_holds_user_and_external_keywords():
    user_kw1 = _kw_usage(
        "u1",
        "user.robot",
        "User KW 1",
        "user.User KW 1",
        "/proj/user.robot",
        file_usages=5,
        total_usages=10,
    )
    user_kw2 = _kw_usage(
        "u2",
        "user.robot",
        "User KW 2",
        "user.User KW 2",
        "/proj/user.robot",
        file_usages=3,
        total_usages=6,
    )
    ext_kw1 = _kw_usage(
        "e1",
        "suite.robot",
        "Click",
        "Browser.Click",
        "/proj/suite.robot",
        file_usages=8,
        total_usages=20,
    )

    resp = MostUsedKeywordsResponse(
        most_used_user_keywords=[user_kw1, user_kw2],
        most_used_external_keywords=[ext_kw1],
    )

    assert len(resp.most_used_user_keywords) == 2
    assert len(resp.most_used_external_keywords) == 1

    user_ids = {k.keyword_id for k in resp.most_used_user_keywords}
    ext_ids = {k.keyword_id for k in resp.most_used_external_keywords}
    assert user_ids == {"u1", "u2"}
    assert ext_ids == {"e1"}


def test_robocop_issue_summary_response_holds_issue_summaries():
    s1 = _issue_summary(RuleCategory.DOC, 5)
    s2 = _issue_summary("Spacing", 3)

    resp = RobocopIssueSummaryResponse(robocop_issue_summary=[s1, s2])

    assert len(resp.robocop_issue_summary) == 2
    categories = [s.category for s in resp.robocop_issue_summary]
    counts = [s.count for s in resp.robocop_issue_summary]

    assert categories[0] == RuleCategory.DOC
    assert categories[1] == "Spacing"
    assert counts == [5, 3]