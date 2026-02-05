from uuid import UUID

from pydantic import ValidationError

from roboview.schemas.domain.keywords import (
    KeywordProperties,
    KeywordUsage,
    SimilarKeyword,
)


def test_keyword_properties_minimal_valid():
    k = KeywordProperties(
        file_name="file.robot",
        keyword_name_without_prefix="My Keyword",
        keyword_name_with_prefix="file.My Keyword",
        is_user_defined=True,
        code="*** Keywords ***\nMy Keyword\n    No Operation",
        source="/proj/file.robot",
        validation_str_without_prefix="mykeyword",
        validation_str_with_prefix="file.mykeyword",
    )

    UUID(k.keyword_id)
    assert k.file_name == "file.robot"
    assert k.keyword_name_without_prefix == "My Keyword"
    assert k.keyword_name_with_prefix == "file.My Keyword"
    assert k.description is None
    assert k.is_user_defined is True
    assert k.code.startswith("*** Keywords ***")
    assert k.source == "/proj/file.robot"
    assert k.validation_str_without_prefix == "mykeyword"
    assert k.validation_str_with_prefix == "file.mykeyword"
    assert k.called_keywords == []


def test_keyword_properties_full_valid_with_called_keywords():
    k = KeywordProperties(
        keyword_id="1234",
        file_name="file.robot",
        keyword_name_without_prefix="Login User",
        keyword_name_with_prefix="file.Login User",
        description="Logs user in",
        is_user_defined=False,
        code="*** Keywords ***\nLogin User\n    No Operation",
        source="/proj/file.robot",
        validation_str_without_prefix="loginuser",
        validation_str_with_prefix="file.loginuser",
        called_keywords=["Open Browser", "Input Credentials"],
    )

    assert k.keyword_id == "1234"
    assert k.called_keywords == ["Open Browser", "Input Credentials"]


def test_keyword_properties_requires_mandatory_fields():
    try:
        KeywordProperties()  # type: ignore[call-arg]
    except ValidationError as exc:
        error_fields = {e["loc"][0] for e in exc.errors()}
        assert "file_name" in error_fields
        assert "keyword_name_without_prefix" in error_fields
        assert "keyword_name_with_prefix" in error_fields
        assert "is_user_defined" in error_fields
        assert "code" in error_fields
        assert "source" in error_fields
        assert "validation_str_without_prefix" in error_fields
        assert "validation_str_with_prefix" in error_fields


def test_keyword_usage_valid():
    u = KeywordUsage(
        keyword_id="kid-1",
        file_name="file.robot",
        keyword_name_without_prefix="My KW",
        keyword_name_with_prefix="file.My KW",
        documentation="Does something",
        source="/proj/file.robot",
        file_usages=2,
        total_usages=5,
    )

    assert u.keyword_id == "kid-1"
    assert u.file_name == "file.robot"
    assert u.keyword_name_without_prefix == "My KW"
    assert u.keyword_name_with_prefix == "file.My KW"
    assert u.documentation == "Does something"
    assert u.source == "/proj/file.robot"
    assert u.file_usages == 2
    assert u.total_usages == 5


def test_keyword_usage_requires_mandatory_fields():
    try:
        KeywordUsage()  # type: ignore[call-arg]
    except ValidationError as exc:
        error_fields = {e["loc"][0] for e in exc.errors()}
        assert error_fields == {
            "keyword_id",
            "file_name",
            "keyword_name_without_prefix",
            "keyword_name_with_prefix",
            "source",
            "file_usages",
            "total_usages",
        }


def test_similar_keyword_valid():
    s = SimilarKeyword(
        keyword_id="kid-1",
        keyword_name_without_prefix="Login User",
        keyword_name_with_prefix="file.Login User",
        source="/proj/file.robot",
        score=87.5,
    )

    assert s.keyword_id == "kid-1"
    assert s.keyword_name_without_prefix == "Login User"
    assert s.keyword_name_with_prefix == "file.Login User"
    assert s.source == "/proj/file.robot"
    assert s.score == 87.5


def test_similar_keyword_requires_mandatory_fields():
    try:
        SimilarKeyword()  # type: ignore[call-arg]
    except ValidationError as exc:
        error_fields = {e["loc"][0] for e in exc.errors()}
        assert error_fields == {
            "keyword_id",
            "keyword_name_without_prefix",
            "keyword_name_with_prefix",
            "source",
            "score",
        }