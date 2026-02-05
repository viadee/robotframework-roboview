import logging

from roboview.registries.robocop_registry import RobocopRegistry
from roboview.schemas.domain.robocop import IssueSummary, RobocopMessage, RuleCategory
from roboview.services.robocop_service import RobocopService, logger


def _msg(
        message_id: str,
        rule_id: str,
        rule_message: str,
        message: str,
        category,
        file_name: str = "file.robot",
        source: str = "/proj/file.robot",
        severity: str = "WARNING",
        code: str = "KW\n    No Operation",
) -> RobocopMessage:
    return RobocopMessage(
        message_id=message_id,
        rule_id=rule_id,
        rule_message=rule_message,
        message=message,
        category=category,
        file_name=file_name,
        source=source,
        severity=severity,
        code=code,
    )


class FakeRobocopRegistry(RobocopRegistry):
    def __init__(self, messages: list[RobocopMessage] | None = None):
        super().__init__()
        if messages:
            for m in messages:
                self.register(m)


def test_get_robocop_error_messages_returns_all_messages():
    m1 = _msg(
        "m1",
        "DOC01",
        "Missing documentation.",
        "Keyword is missing documentation.",
        RuleCategory.DOC,
    )
    m2 = _msg(
        "m2",
        "ARG01",
        "Too many arguments.",
        "Keyword has too many arguments.",
        RuleCategory.ARG,
    )

    reg = FakeRobocopRegistry([m1, m2])
    svc = RobocopService(reg)

    result = svc.get_robocop_error_messages()

    assert len(result) == 2
    ids = {m.message_id for m in result}
    assert ids == {"m1", "m2"}


def test_get_robocop_error_messages_handles_exception_and_returns_empty(monkeypatch, caplog):
    reg = FakeRobocopRegistry([])
    svc = RobocopService(reg)

    def broken_get_all():
        raise RuntimeError("boom")

    monkeypatch.setattr(reg, "get_all_error_messages", broken_get_all, raising=True)

    caplog.set_level(logging.ERROR, logger=logger.name)

    result = svc.get_robocop_error_messages()

    assert result == []
    assert any(
        "Failed to get robocop error messages" in r.getMessage()
        for r in caplog.records
    )


def test_get_robocop_message_by_id_happy_path():
    m1 = _msg(
        "m1",
        "DOC01",
        "Missing documentation.",
        "Keyword is missing documentation.",
        RuleCategory.DOC,
    )
    reg = FakeRobocopRegistry([m1])
    svc = RobocopService(reg)

    result = svc.get_robocop_message_by_id("m1")

    assert isinstance(result, RobocopMessage)
    assert result.message_id == "m1"
    assert result.rule_id == "DOC01"


def test_get_robocop_message_by_id_empty_id_logs_warning_and_returns_none(caplog):
    reg = FakeRobocopRegistry([])
    svc = RobocopService(reg)

    caplog.set_level(logging.WARNING, logger=logger.name)

    result = svc.get_robocop_message_by_id("")

    assert result is None
    assert any(
        "Empty message_id provided to get_robocop_message_by_id" in r.getMessage()
        for r in caplog.records
    )


def test_get_robocop_message_by_id_handles_exception_and_returns_none(monkeypatch, caplog):
    m1 = _msg(
        "m1",
        "DOC01",
        "Missing documentation.",
        "Keyword is missing documentation.",
        RuleCategory.DOC,
    )
    reg = FakeRobocopRegistry([m1])
    svc = RobocopService(reg)

    def broken_resolve(mid: str):
        raise RuntimeError("boom")

    monkeypatch.setattr(reg, "resolve", broken_resolve, raising=True)

    caplog.set_level(logging.ERROR, logger=logger.name)

    result = svc.get_robocop_message_by_id("m1")

    assert result is None
    assert any(
        "Failed to get robocop message by id 'm1'" in r.getMessage()
        for r in caplog.records
    )


def test_get_robocop_issue_summary_happy_path():
    m1 = _msg(
        "m1",
        "DOC01",
        "Missing documentation.",
        "Keyword is missing documentation.",
        RuleCategory.DOC,
    )
    m2 = _msg(
        "m2",
        "DOC01",
        "Missing documentation.",
        "Another missing documentation.",
        RuleCategory.DOC,
    )
    m3 = _msg(
        "m3",
        "ARG01",
        "Too many arguments.",
        "Keyword has too many arguments.",
        RuleCategory.ARG,
    )
    m4 = _msg(
        "m4",
        "MISC01",
        "Some misc issue.",
        "Misc message.",
        "Miscellaneous",
    )

    reg = FakeRobocopRegistry([m1, m2, m3, m4])
    svc = RobocopService(reg)

    summary = svc.get_robocop_issue_summary()

    assert len(summary) == 3
    assert all(isinstance(s, IssueSummary) for s in summary)

    by_cat = {s.category: s.count for s in summary}
    assert by_cat[RuleCategory.DOC] == 2
    assert by_cat[RuleCategory.ARG] == 1
    assert by_cat["Miscellaneous"] == 1

    counts = [s.count for s in summary]
    assert counts == sorted(counts, reverse=True)


def test_get_robocop_issue_summary_no_errors_logs_info_and_returns_empty(caplog):
    reg = FakeRobocopRegistry([])
    svc = RobocopService(reg)

    caplog.set_level(logging.INFO, logger=logger.name)

    summary = svc.get_robocop_issue_summary()

    assert summary == []
    assert any(
        "No robocop error messages found for issue summary" in r.getMessage()
        for r in caplog.records
    )


def test_get_robocop_issue_summary_handles_registry_exception(monkeypatch, caplog):
    reg = FakeRobocopRegistry([])
    svc = RobocopService(reg)

    def broken_get_all():
        raise RuntimeError("boom")

    monkeypatch.setattr(reg, "get_all_error_messages", broken_get_all, raising=True)

    caplog.set_level(logging.ERROR, logger=logger.name)

    summary = svc.get_robocop_issue_summary()

    assert summary == []
    assert any(
        "Failed to get robocop issue summary" in r.getMessage()
        for r in caplog.records
    )