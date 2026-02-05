import logging

from robot.parsing.model.statements import (
    KeywordCall,
    Setup,
    Teardown,
    TestSetup,
    TestTeardown,
)

from roboview.models.robot_parsing.called_keyword_parsing import (
    CalledKeywordFinder,
    logger,
)


def _make_keyword_call(text: str) -> KeywordCall:
    return KeywordCall.from_params(text)


def _make_setup(text: str) -> Setup:
    return Setup.from_params(text)


def _make_teardown(text: str) -> Teardown:
    return Teardown.from_params(text)


def _make_test_setup(text: str) -> TestSetup:
    return TestSetup.from_params(text)


def _make_test_teardown(text: str) -> TestTeardown:
    return TestTeardown.from_params(text)


def test_called_keyword_finder_initial_state():
    finder = CalledKeywordFinder()
    assert finder.called_keywords == []
    assert finder.bdd_prefixes == ["given", "when", "then", "and", "but"]


def test_add_keyword_simple():
    finder = CalledKeywordFinder()
    finder._add_keyword("Login User")
    assert finder.called_keywords == ["Login User"]


def test_add_keyword_with_bdd_prefix():
    finder = CalledKeywordFinder()
    finder._add_keyword("Given Login User")
    finder._add_keyword("when Search Product")
    finder._add_keyword("Then Verify Result")
    assert finder.called_keywords == [
        "Login User",
        "Search Product",
        "Verify Result",
    ]


def test_add_keyword_with_unknown_prefix():
    finder = CalledKeywordFinder()
    finder._add_keyword("Background Setup Environment")
    assert finder.called_keywords == ["Background Setup Environment"]


def test_ignore_bdd_prefixes_happy_paths():
    finder = CalledKeywordFinder()

    assert finder._ignore_bdd_prefixes("Given Login User") == "Login User"
    assert finder._ignore_bdd_prefixes("when  Search Product") == "Search Product"
    assert finder._ignore_bdd_prefixes("THEN  Verify Result") == "Verify Result"

    assert finder._ignore_bdd_prefixes("Log To Console") == "Log To Console"
    assert finder._ignore_bdd_prefixes("And") == "And"
    assert finder._ignore_bdd_prefixes("   ") == "   "


def test_add_keyword_error_logging(monkeypatch, caplog):
    finder = CalledKeywordFinder()

    def _raise_error(raw_name: str) -> str:
        raise RuntimeError("boom")

    monkeypatch.setattr(
        finder,
        "_ignore_bdd_prefixes",
        _raise_error,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    finder._add_keyword("Given Something")

    assert any(
        "Error while adding node to keyword list" in record.getMessage()
        for record in caplog.records
    )


def test_visit_keyword_call():
    finder = CalledKeywordFinder()
    node = _make_keyword_call("Login User")
    finder.visit_KeywordCall(node)
    assert finder.called_keywords == ["Login User"]


def test_visit_keyword_call_with_bdd_prefix():
    finder = CalledKeywordFinder()
    node = _make_keyword_call("Given Login User")
    finder.visit_KeywordCall(node)
    assert finder.called_keywords == ["Login User"]


def test_visit_setup():
    finder = CalledKeywordFinder()
    node = _make_setup("Suite Setup Keyword")
    finder.visit_Setup(node)
    assert finder.called_keywords == ["Suite Setup Keyword"]


def test_visit_teardown():
    finder = CalledKeywordFinder()
    node = _make_teardown("Suite Teardown Keyword")
    finder.visit_Teardown(node)
    assert finder.called_keywords == ["Suite Teardown Keyword"]


def test_visit_test_setup():
    finder = CalledKeywordFinder()
    node = _make_test_setup("Test Setup Keyword")
    finder.visit_TestSetup(node)
    assert finder.called_keywords == ["Test Setup Keyword"]


def test_visit_test_teardown():
    finder = CalledKeywordFinder()
    node = _make_test_teardown("Test Teardown Keyword")
    finder.visit_TestTeardown(node)
    assert finder.called_keywords == ["Test Teardown Keyword"]


def test_visit_multiple_nodes_integration():
    finder = CalledKeywordFinder()

    finder.visit_KeywordCall(_make_keyword_call("Given Login User"))
    finder.visit_KeywordCall(_make_keyword_call("Search Product"))
    finder.visit_Setup(_make_setup("Suite Setup Keyword"))
    finder.visit_Teardown(_make_teardown("Suite Teardown Keyword"))
    finder.visit_TestSetup(_make_test_setup("Test Setup Keyword"))
    finder.visit_TestTeardown(_make_test_teardown("Test Teardown Keyword"))

    assert finder.called_keywords == [
        "Login User",
        "Search Product",
        "Suite Setup Keyword",
        "Suite Teardown Keyword",
        "Test Setup Keyword",
        "Test Teardown Keyword",
    ]