import logging
from pathlib import Path

from robot.parsing.model.statements import KeywordCall

from roboview.models.robot_parsing.keyword_dependency_parsing import (
    KeywordDependencyFinder,
    logger,
)


class FakeKeywordNode:
    def __init__(self, name: str, body: list | None = None) -> None:
        self.name = name
        self.body = body or []


def _make_keyword(name: str, body: list | None = None) -> FakeKeywordNode:
    return FakeKeywordNode(name=name, body=body)


def _make_keyword_call(name: str | None) -> KeywordCall:
    if not name:
        return KeywordCall.from_params("")
    return KeywordCall.from_params(name)


def test_initial_state():
    finder = KeywordDependencyFinder(Path("/path/to/file.robot"))
    assert finder.keyword_calls == {}
    assert finder.file_path == Path("/path/to/file.robot")


def test_visit_keyword_sets_context_and_collects_calls(monkeypatch):
    finder = KeywordDependencyFinder(Path("/path/to/file.robot"))

    body = [
        _make_keyword_call("Login"),
        _make_keyword_call("Open Browser"),
        _make_keyword_call("Login"),
    ]
    kw_node = _make_keyword("Setup Environment", body=body)

    def fake_generic_visit(node):
        for child in getattr(node, "body", []) or []:
            if isinstance(child, KeywordCall):
                finder.visit_KeywordCall(child)

    monkeypatch.setattr(finder, "generic_visit", fake_generic_visit)

    finder.visit_Keyword(kw_node)

    assert finder.current_keyword == "Setup Environment"
    assert finder.keyword_calls["Setup Environment"] == [
        "Login",
        "Open Browser",
        "Login",
    ]

    formatted = finder.get_formatted_result()
    assert len(formatted) == 1
    entry = formatted[0]

    assert entry["file_path"] == "/path/to/file.robot"
    assert entry["file_name"] == "file.robot"
    assert entry["keyword_name"] == "Setup Environment"
    assert sorted(entry["called_keywords"]) == ["Login", "Open Browser"]


def test_visit_multiple_keywords_builds_mapping(monkeypatch):
    finder = KeywordDependencyFinder(Path("/project/resources/common.resource"))

    def fake_generic_visit(node):
        for child in getattr(node, "body", []) or []:
            if isinstance(child, KeywordCall):
                finder.visit_KeywordCall(child)

    monkeypatch.setattr(finder, "generic_visit", fake_generic_visit)

    kw1 = _make_keyword(
        "Login User",
        body=[
            _make_keyword_call("Open Browser"),
            _make_keyword_call("Input Credentials"),
            _make_keyword_call("Submit Form"),
        ],
    )

    kw2 = _make_keyword(
        "Logout User",
        body=[
            _make_keyword_call("Click Logout"),
            _make_keyword_call("Close Browser"),
        ],
    )

    finder.visit_Keyword(kw1)
    finder.visit_Keyword(kw2)

    assert set(finder.keyword_calls.keys()) == {"Login User", "Logout User"}
    assert finder.keyword_calls["Login User"] == [
        "Open Browser",
        "Input Credentials",
        "Submit Form",
    ]
    assert finder.keyword_calls["Logout User"] == [
        "Click Logout",
        "Close Browser",
    ]

    formatted = finder.get_formatted_result()
    assert len(formatted) == 2

    by_name = {e["keyword_name"]: e for e in formatted}
    assert sorted(by_name["Login User"]["called_keywords"]) == [
        "Input Credentials",
        "Open Browser",
        "Submit Form",
    ]
    assert sorted(by_name["Logout User"]["called_keywords"]) == [
        "Click Logout",
        "Close Browser",
    ]


def test_visit_keyword_handles_missing_name_attribute(caplog):
    class NoNameKeyword:
        def __init__(self) -> None:
            self.body = []

    finder = KeywordDependencyFinder(Path("/path/to/file.robot"))

    caplog.set_level(logging.ERROR, logger=logger.name)

    node = NoNameKeyword()
    finder.visit_Keyword(node)  # type: ignore[arg-type]

    assert finder.keyword_calls == {}
    assert any(
        "Keyword node missing expected name attribute" in record.getMessage()
        for record in caplog.records
    )


def test_visit_keyword_logs_unexpected_error(monkeypatch, caplog):
    finder = KeywordDependencyFinder(Path("/path/to/file.robot"))

    kw = _make_keyword("Some Keyword")

    def broken_generic_visit(node):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        finder,
        "generic_visit",
        broken_generic_visit,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    finder.visit_Keyword(kw)

    assert "Some Keyword" in finder.keyword_calls
    assert finder.keyword_calls["Some Keyword"] == []
    assert any(
        "Unexpected error while visiting keyword: Some Keyword" in record.getMessage()
        for record in caplog.records
    )


def test_visit_keyword_call_ignores_when_no_current_keyword():
    finder = KeywordDependencyFinder(Path("/path/to/file.robot"))
    if hasattr(finder, "current_keyword"):
        delattr(finder, "current_keyword")

    call = _make_keyword_call("Login")

    try:
        finder.visit_KeywordCall(call)
    except AttributeError:
        pass

    assert finder.keyword_calls == {}


def test_visit_keyword_call_collects_calls_for_current_keyword(monkeypatch):
    finder = KeywordDependencyFinder(Path("/path/to/file.robot"))

    def fake_generic_visit(node):
        for child in getattr(node, "body", []) or []:
            if isinstance(child, KeywordCall):
                finder.visit_KeywordCall(child)

    monkeypatch.setattr(finder, "generic_visit", fake_generic_visit)

    kw = _make_keyword("Wrapper Keyword", body=[_make_keyword_call("Inner 1")])
    finder.visit_Keyword(kw)

    call2 = _make_keyword_call("Inner 2")
    finder.visit_KeywordCall(call2)

    assert finder.keyword_calls["Wrapper Keyword"] == ["Inner 1", "Inner 2"]


def test_visit_keyword_call_ignores_empty_keyword_names():
    finder = KeywordDependencyFinder(Path("/path/to/file.robot"))

    kw = _make_keyword("Wrapper Keyword")
    finder.visit_Keyword(kw)

    empty_call = _make_keyword_call("")
    none_call = _make_keyword_call(None)

    finder.visit_KeywordCall(empty_call)
    finder.visit_KeywordCall(none_call)

    assert finder.keyword_calls["Wrapper Keyword"] == []


def test_visit_keyword_call_logs_missing_keyword_attribute(caplog):
    class NoKeywordAttr:
        pass

    finder = KeywordDependencyFinder(Path("/path/to/file.robot"))
    finder.current_keyword = "Some Keyword"  # type: ignore[assignment]

    caplog.set_level(logging.ERROR, logger=logger.name)

    node = NoKeywordAttr()
    finder.visit_KeywordCall(node)  # type: ignore[arg-type]

    assert any(
        "KeywordCall node missing expected keyword attribute" in record.getMessage()
        for record in caplog.records
    )


def test_visit_keyword_call_logs_unexpected_error(monkeypatch, caplog):
    finder = KeywordDependencyFinder(Path("/path/to/file.robot"))

    kw = _make_keyword("Wrapper Keyword", body=[_make_keyword_call("Inner Keyword")])
    finder.visit_Keyword(kw)

    call = _make_keyword_call("Broken")

    def broken_keyword_getter(self):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        call.__class__,
        "keyword",
        property(broken_keyword_getter),
        raising=True,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    finder.visit_KeywordCall(call)

    assert any(
        "Unexpected error while processing keyword call in keyword: Wrapper Keyword"
        in record.getMessage()
        for record in caplog.records
    )


def test_get_formatted_result_handles_exception(monkeypatch, caplog):
    finder = KeywordDependencyFinder(Path("/path/to/file.robot"))
    finder.keyword_calls = {"K1": ["A", "B"]}

    def broken_items():
        raise RuntimeError("boom")

    class FakeDict(dict):
        def items(self):
            return broken_items()

    finder.keyword_calls = FakeDict(finder.keyword_calls)

    caplog.set_level(logging.ERROR, logger=logger.name)

    result = finder.get_formatted_result()
    assert result == []
    assert any(
        "Error while formatting keyword dependency results" in record.getMessage()
        for record in caplog.records
    )