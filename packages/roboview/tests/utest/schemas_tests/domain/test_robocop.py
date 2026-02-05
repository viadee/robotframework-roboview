from uuid import UUID

from pydantic import ValidationError

from roboview.schemas.domain.robocop import RuleCategory, RobocopMessage, IssueSummary


def test_rule_category_values_and_members():
    assert RuleCategory.ARG.value == "Arguments"
    assert RuleCategory.COM.value == "Comments"
    assert RuleCategory.DEPR.value == "Deprecated"
    assert RuleCategory.DOC.value == "Documentation"
    assert RuleCategory.DUP.value == "Duplication"
    assert RuleCategory.ERR.value == "Errors"
    assert RuleCategory.IMP.value == "Imports"
    assert RuleCategory.KW.value == "Keywords"
    assert RuleCategory.LEN.value == "Lengths"
    assert RuleCategory.MISC.value == "Miscellaneous"
    assert RuleCategory.NAME.value == "Naming"
    assert RuleCategory.ORD.value == "Order"
    assert RuleCategory.SPC.value == "Spacing"
    assert RuleCategory.TAG.value == "Tags"
    assert RuleCategory.VAR.value == "Variables"
    assert RuleCategory.ANN.value == "Annotations"

    assert set(RuleCategory.__members__.keys()) == {
        "ARG",
        "COM",
        "DEPR",
        "DOC",
        "DUP",
        "ERR",
        "IMP",
        "KW",
        "LEN",
        "MISC",
        "NAME",
        "ORD",
        "SPC",
        "TAG",
        "VAR",
        "ANN",
    }


def test_robocop_message_minimal_valid_with_enum_category():
    msg = RobocopMessage(
        rule_id="0201",
        rule_message="Keyword name does not follow naming convention.",
        message="Keyword 'mykey' should be in Title Case.",
        category=RuleCategory.NAME,
        file_name="file.robot",
        source="/proj/file.robot",
        severity="WARNING",
        code="*** Keywords ***\nmykey\n    No Operation",
    )

    UUID(msg.message_id)
    assert msg.rule_id == "0201"
    assert msg.rule_message.startswith("Keyword name")
    assert msg.message.startswith("Keyword 'mykey'")
    assert msg.category == RuleCategory.NAME
    assert msg.file_name == "file.robot"
    assert msg.source == "/proj/file.robot"
    assert msg.severity == "WARNING"
    assert "mykey" in msg.code


def test_robocop_message_accepts_string_category():
    msg = RobocopMessage(
        rule_id="0501",
        rule_message="Too many arguments.",
        message="Keyword has 10 arguments.",
        category="Arguments",
        file_name="file.robot",
        source="/proj/file.robot",
        severity="ERROR",
        code="My KW    ${a}    ${b}",
    )

    assert msg.category == "Arguments"


def test_robocop_message_requires_mandatory_fields():
    try:
        RobocopMessage()  # type: ignore[call-arg]
    except ValidationError as exc:
        error_fields = {e["loc"][0] for e in exc.errors()}
        assert "rule_id" in error_fields
        assert "rule_message" in error_fields
        assert "message" in error_fields
        assert "category" in error_fields
        assert "file_name" in error_fields
        assert "source" in error_fields
        assert "severity" in error_fields
        assert "code" in error_fields


def test_issue_summary_with_enum_category():
    summary = IssueSummary(
        category=RuleCategory.ERR,
        count=5,
    )

    assert summary.category == RuleCategory.ERR
    assert summary.count == 5


def test_issue_summary_with_string_category():
    summary = IssueSummary(
        category="Documentation",
        count=3,
    )

    assert summary.category == "Documentation"
    assert summary.count == 3


def test_issue_summary_requires_mandatory_fields():
    try:
        IssueSummary()  # type: ignore[call-arg]
    except ValidationError as exc:
        error_fields = {e["loc"][0] for e in exc.errors()}
        assert error_fields == {"category", "count"}