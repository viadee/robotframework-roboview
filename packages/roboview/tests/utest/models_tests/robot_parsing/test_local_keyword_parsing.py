import logging
from pathlib import Path

from robot.parsing.model.blocks import Keyword, ModelWriter
from robot.parsing.model.statements import Documentation, KeywordCall

from roboview.models.robot_parsing.local_keyword_parsing import (
    LocalKeywordFinder,
    LocalKeywordNameFinder,
    logger,
)
from roboview.schemas.domain.keywords import KeywordProperties


class FakeKeywordNode:
    def __init__(self, name: str, body: list | None = None) -> None:
        self.name = name
        self.body = body or []


def _make_keyword(name: str, body: list | None = None) -> FakeKeywordNode:
    return FakeKeywordNode(name=name, body=body)


def _make_documentation(value: str) -> Documentation:
    try:
        return Documentation.from_params(value)
    except AttributeError:
        doc = Documentation()
        doc.value = value
        return doc


def test_local_keyword_finder_initial_state():
    path = Path("/path/to/file.robot")
    finder = LocalKeywordFinder(path)

    assert finder.keyword_doc == []
    assert finder.file_path == path


def test_local_keyword_finder_collects_basic_keyword_without_doc(monkeypatch):
    path = Path("/path/to/file.robot")
    finder = LocalKeywordFinder(path)

    kw = _make_keyword("My Keyword")

    def fake_convert(node: Keyword) -> str:
        return f"*** Keywords ***\n{node.name}\n"

    monkeypatch.setattr(
        finder,
        "convert_keyword_ast_to_string",
        fake_convert,
    )

    finder.visit_Keyword(kw)  # type: ignore[arg-type]

    assert len(finder.keyword_doc) == 1
    props = finder.keyword_doc[0]
    assert isinstance(props, KeywordProperties)

    assert props.file_name == "file.robot"
    assert props.keyword_name_without_prefix == "My Keyword"
    assert props.keyword_name_with_prefix == "file.My Keyword"
    assert props.description == ""
    assert props.is_user_defined is True
    assert props.code == "*** Keywords ***\nMy Keyword\n"
    assert props.source == "/path/to/file.robot"
    assert props.validation_str_without_prefix == "mykeyword"
    assert props.validation_str_with_prefix == "file.mykeyword"


def test_local_keyword_finder_collects_keyword_with_documentation(monkeypatch):
    path = Path("/project/resources/common.resource")
    finder = LocalKeywordFinder(path)

    doc = _make_documentation("This is a keyword.")
    body = [doc, KeywordCall.from_params("Do Something")]
    kw = _make_keyword("Setup Env", body=body)

    monkeypatch.setattr(
        finder,
        "convert_keyword_ast_to_string",
        lambda node: f"KW: {node.name}",
    )

    finder.visit_Keyword(kw)  # type: ignore[arg-type]

    assert len(finder.keyword_doc) == 1
    props = finder.keyword_doc[0]

    assert props.file_name == "common.resource"
    assert props.keyword_name_without_prefix == "Setup Env"
    assert props.keyword_name_with_prefix == "common.Setup Env"
    assert props.description == "This is a keyword."
    assert props.code == "KW: Setup Env"
    assert props.source == "/project/resources/common.resource"
    assert props.validation_str_without_prefix == "setupenv"
    assert props.validation_str_with_prefix == "common.setupenv"


def test_local_keyword_finder_handles_multiple_keywords(monkeypatch):
    path = Path("/proj/tests/file.robot")
    finder = LocalKeywordFinder(path)

    kw1 = _make_keyword(
        "First Keyword",
        body=[_make_documentation("First doc")],
    )
    kw2 = _make_keyword(
        "Second_Keyword",
        body=[_make_documentation("Second doc")],
    )

    monkeypatch.setattr(
        finder,
        "convert_keyword_ast_to_string",
        lambda node: f"KW: {node.name}",
    )

    finder.visit_Keyword(kw1)  # type: ignore[arg-type]
    finder.visit_Keyword(kw2)  # type: ignore[arg-type]

    assert len(finder.keyword_doc) == 2

    names = {k.keyword_name_without_prefix for k in finder.keyword_doc}
    assert names == {"First Keyword", "Second_Keyword"}

    by_name = {k.keyword_name_without_prefix: k for k in finder.keyword_doc}
    assert by_name["First Keyword"].description == "First doc"
    assert by_name["Second_Keyword"].description == "Second doc"

    assert by_name["First Keyword"].validation_str_without_prefix == "firstkeyword"
    assert by_name["Second_Keyword"].validation_str_without_prefix == "secondkeyword"


def test_local_keyword_finder_logs_attribute_error(caplog):
    class NoNameKeyword:
        def __init__(self) -> None:
            self.body = []

    path = Path("/path/to/file.robot")
    finder = LocalKeywordFinder(path)

    caplog.set_level(logging.ERROR, logger=logger.name)

    node = NoNameKeyword()
    finder.visit_Keyword(node)  # type: ignore[arg-type]

    assert finder.keyword_doc == []
    assert any(
        "Keyword node missing expected attributes" in record.getMessage()
        for record in caplog.records
    )


def test_local_keyword_finder_logs_unexpected_error(monkeypatch, caplog):
    path = Path("/path/to/file.robot")
    finder = LocalKeywordFinder(path)

    kw = _make_keyword("Some Keyword")

    def broken_convert(node: Keyword) -> str:
        raise RuntimeError("boom")

    monkeypatch.setattr(
        finder,
        "convert_keyword_ast_to_string",
        broken_convert,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    finder.visit_Keyword(kw)  # type: ignore[arg-type]

    assert len(finder.keyword_doc) == 0
    assert any(
        "Unexpected error while visiting keyword" in record.getMessage()
        for record in caplog.records
    )


def test_convert_keyword_ast_to_string_success(monkeypatch):
    kw = _make_keyword("My KW")

    class FakeWriter(ModelWriter):
        def __init__(self, output):
            self.output = output

        def write(self, node):
            self.output.write(f"FAKE:{node.name}")

    monkeypatch.setattr(
        "roboview.models.robot_parsing.local_keyword_parsing.ModelWriter",
        FakeWriter,
        raising=True,
    )

    result = LocalKeywordFinder.convert_keyword_ast_to_string(kw)  # type: ignore[arg-type]
    assert result == "FAKE:My KW"


def test_convert_keyword_ast_to_string_falls_back_to_name_on_error(monkeypatch, caplog):
    kw = _make_keyword("BrokenKW")

    class BrokenWriter(ModelWriter):
        def __init__(self, output):
            self.output = output

        def write(self, node):
            raise RuntimeError("boom")

    monkeypatch.setattr(
        "roboview.models.robot_parsing.local_keyword_parsing.ModelWriter",
        BrokenWriter,
        raising=True,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    result = LocalKeywordFinder.convert_keyword_ast_to_string(kw)  # type: ignore[arg-type]
    assert result == "BrokenKW"
    assert any(
        "Failed to convert node to string" in record.getMessage()
        for record in caplog.records
    )


def test_local_keyword_name_finder_initial_state():
    finder = LocalKeywordNameFinder()
    assert finder.keywords == []


def test_local_keyword_name_finder_collects_keyword_names():
    finder = LocalKeywordNameFinder()

    kw1 = _make_keyword("Login User")
    kw2 = _make_keyword("logout user")

    finder.visit_Keyword(kw1)  # type: ignore[arg-type]
    finder.visit_Keyword(kw2)  # type: ignore[arg-type]

    assert finder.keywords == ["Login User", "logout user"]


def test_local_keyword_name_finder_logs_missing_name_attribute(caplog):
    class NoNameKeyword:
        def __init__(self) -> None:
            self.body = []

    finder = LocalKeywordNameFinder()

    caplog.set_level(logging.ERROR, logger=logger.name)

    node = NoNameKeyword()
    finder.visit_Keyword(node)  # type: ignore[arg-type]

    assert finder.keywords == []
    assert any(
        "Keyword node missing 'name' attribute" in record.getMessage()
        for record in caplog.records
    )


def test_local_keyword_name_finder_logs_unexpected_error(monkeypatch, caplog):
    class FakeList(list):
        def append(self, name):
            raise RuntimeError("boom")

    finder = LocalKeywordNameFinder()
    finder.keywords = FakeList()  # type: ignore[assignment]

    kw = _make_keyword("Some KW")

    caplog.set_level(logging.ERROR, logger=logger.name)

    finder.visit_Keyword(kw)  # type: ignore[arg-type]

    assert finder.keywords == []
    assert any(
        "Unexpected error while visiting keyword" in record.getMessage()
        for record in caplog.records
    )