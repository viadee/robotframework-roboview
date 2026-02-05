from roboview.schemas.domain.robocop import RobocopMessage, RuleCategory
from roboview.schemas.dtos.robocop import (
    RobocopMessageResponse,
    RobocopMessagesResponse,
    RobocopMessagesByCategoryResponse,
)


def _msg(
        rule_id: str,
        rule_message: str,
        message: str,
        category,
        file_name: str,
        source: str,
        severity: str,
        code: str,
) -> RobocopMessage:
    return RobocopMessage(
        rule_id=rule_id,
        rule_message=rule_message,
        message=message,
        category=category,
        file_name=file_name,
        source=source,
        severity=severity,
        code=code,
    )


def test_robocop_message_response_wraps_single_message():
    m = _msg(
        rule_id="0201",
        rule_message="Keyword name does not follow naming convention.",
        message="Keyword 'mykey' should be in Title Case.",
        category=RuleCategory.NAME,
        file_name="file.robot",
        source="/proj/file.robot",
        severity="WARNING",
        code="*** Keywords ***\nmykey\n    No Operation",
    )

    resp = RobocopMessageResponse(message=m)

    assert isinstance(resp.message, RobocopMessage)
    assert resp.message.rule_id == "0201"
    assert resp.message.category == RuleCategory.NAME
    assert resp.message.file_name == "file.robot"


def test_robocop_messages_response_wraps_list_of_messages():
    m1 = _msg(
        rule_id="0501",
        rule_message="Too many arguments.",
        message="Keyword has 10 arguments.",
        category="Arguments",
        file_name="a.robot",
        source="/proj/a.robot",
        severity="ERROR",
        code="My KW    ${a}    ${b}",
    )
    m2 = _msg(
        rule_id="0301",
        rule_message="Keyword is deprecated.",
        message="Keyword 'Old KW' is deprecated.",
        category=RuleCategory.DEPR,
        file_name="b.robot",
        source="/proj/b.robot",
        severity="WARNING",
        code="Old KW",
    )

    resp = RobocopMessagesResponse(messages=[m1, m2])

    assert len(resp.messages) == 2
    rule_ids = [m.rule_id for m in resp.messages]
    assert rule_ids == ["0501", "0301"]
    assert resp.messages[0].category == "Arguments"
    assert resp.messages[1].category == RuleCategory.DEPR


def test_robocop_messages_by_category_response_wraps_messages():
    m1 = _msg(
        rule_id="D001",
        rule_message="Missing documentation.",
        message="Keyword is missing documentation.",
        category=RuleCategory.DOC,
        file_name="a.robot",
        source="/proj/a.robot",
        severity="INFO",
        code="Some KW",
    )
    m2 = _msg(
        rule_id="D002",
        rule_message="Too short documentation.",
        message="Documentation is too short.",
        category=RuleCategory.DOC,
        file_name="b.robot",
        source="/proj/b.robot",
        severity="WARNING",
        code="Another KW",
    )

    resp = RobocopMessagesByCategoryResponse(messages_by_category=[m1, m2])

    assert len(resp.messages_by_category) == 2
    assert all(m.category == RuleCategory.DOC for m in resp.messages_by_category)
    filenames = {m.file_name for m in resp.messages_by_category}
    assert filenames == {"a.robot", "b.robot"}