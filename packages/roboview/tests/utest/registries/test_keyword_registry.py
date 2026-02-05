import logging

import pytest

from roboview.registries.keyword_registry import KeywordRegistry, logger
from roboview.schemas.domain.keywords import KeywordProperties


def _make_keyword(
        keyword_id: str,
        file_name: str = "file.robot",
        keyword_name_without_prefix: str = "My Keyword",
        keyword_name_with_prefix: str | None = "file.My Keyword",
        description: str = "",
        is_user_defined: bool = True,
        code: str = "",
        source: str = "/path/to/file.robot",
        validation_str_without_prefix: str | None = None,
        validation_str_with_prefix: str | None = None,
) -> KeywordProperties:
    base_without = keyword_name_without_prefix.lower().replace(" ", "").replace("_", "")
    base_with = (
        (keyword_name_with_prefix or keyword_name_without_prefix)
        .lower()
        .replace(" ", "")
        .replace("_", "")
    )
    return KeywordProperties(
        keyword_id=keyword_id,
        file_name=file_name,
        keyword_name_without_prefix=keyword_name_without_prefix,
        keyword_name_with_prefix=keyword_name_with_prefix,
        description=description,
        is_user_defined=is_user_defined,
        code=code,
        source=source,
        validation_str_without_prefix=validation_str_without_prefix or base_without,
        validation_str_with_prefix=validation_str_with_prefix or base_with,
    )


def test_initial_state():
    registry = KeywordRegistry()
    assert len(registry) == 0
    assert registry.get_all_keywords() == []
    assert registry.get_user_defined_keywords() == []
    assert registry.get_non_user_defined_keywords() == []


def test_register_adds_keyword_and_len_and_get_all_keywords_reflect_it():
    registry = KeywordRegistry()

    k1 = _make_keyword("k1", keyword_name_without_prefix="Login")
    k2 = _make_keyword("k2", keyword_name_without_prefix="Logout", is_user_defined=False)

    registry.register(k1)
    registry.register(k2)

    assert len(registry) == 2
    all_keywords = registry.get_all_keywords()
    assert set(k.keyword_id for k in all_keywords) == {"k1", "k2"}


def test_register_overwrites_existing_same_id():
    registry = KeywordRegistry()

    k1 = _make_keyword("k1", keyword_name_without_prefix="Old Name")
    k2 = _make_keyword("k1", keyword_name_without_prefix="New Name")

    registry.register(k1)
    registry.register(k2)

    all_keywords = registry.get_all_keywords()
    assert len(all_keywords) == 1
    assert all_keywords[0].keyword_name_without_prefix == "New Name"


def test_resolve_by_prefixed_and_unprefixed_name():
    registry = KeywordRegistry()

    k = _make_keyword(
        "k1",
        file_name="file.robot",
        keyword_name_without_prefix="Login User",
        keyword_name_with_prefix="file.Login User",
    )
    registry.register(k)

    resolved_prefixed = registry.resolve("file.Login User")
    resolved_unprefixed = registry.resolve("Login User")

    assert resolved_prefixed is k
    assert resolved_unprefixed is k


def test_resolve_is_case_insensitive_and_ignores_spaces_and_underscores():
    registry = KeywordRegistry()

    k = _make_keyword(
        "k1",
        keyword_name_without_prefix="Login User",
        keyword_name_with_prefix="MyRes.Login User",
        validation_str_without_prefix="loginuser",
        validation_str_with_prefix="myres.loginuser",
    )
    registry.register(k)

    assert registry.resolve("myres.login_user") is k
    assert registry.resolve("myres.LOGIN USER") is k
    assert registry.resolve("login_user") is k
    assert registry.resolve("LOGIN USER") is k


def test_resolve_returns_none_for_unknown_keyword():
    registry = KeywordRegistry()

    k = _make_keyword("k1", keyword_name_without_prefix="Known")
    registry.register(k)

    assert registry.resolve("Unknown") is None


def test_resolve_handles_empty_keyword_name_and_logs_warning(caplog):
    registry = KeywordRegistry()

    caplog.set_level(logging.WARNING, logger=logger.name)

    result = registry.resolve("")
    assert result is None

    assert any(
        "Empty keyword_name provided to resolve()" in record.getMessage()
        for record in caplog.records
    )


def test_resolve_logs_exception_and_returns_none_on_error(monkeypatch, caplog):
    registry = KeywordRegistry()
    k = _make_keyword("k1", keyword_name_without_prefix="Login")
    registry.register(k)

    def broken_get_all():
        raise RuntimeError("boom")

    monkeypatch.setattr(registry, "get_all_keywords", broken_get_all, raising=True)

    caplog.set_level(logging.ERROR, logger=logger.name)

    result = registry.resolve("Login")
    assert result is None
    assert any(
        "Error while resolving keyword: Login" in record.getMessage()
        for record in caplog.records
    )


def test_get_prefix_variants_returns_both_variants_when_found():
    registry = KeywordRegistry()

    k = _make_keyword(
        "k1",
        keyword_name_without_prefix="Login User",
        keyword_name_with_prefix="file.Login User",
    )
    registry.register(k)

    prefixed, unprefixed = registry.get_prefix_variants("Login User")
    assert prefixed == "file.Login User"
    assert unprefixed == "Login User"

    prefixed2, unprefixed2 = registry.get_prefix_variants("file.Login User")
    assert prefixed2 == "file.Login User"
    assert unprefixed2 == "Login User"


def test_get_prefix_variants_returns_original_when_not_found_and_logs_warning(caplog):
    registry = KeywordRegistry()

    caplog.set_level(logging.WARNING, logger=logger.name)

    prefixed, unprefixed = registry.get_prefix_variants("Unknown KW")
    assert prefixed == "Unknown KW"
    assert unprefixed == "Unknown KW"

    assert any(
        "Keyword not found in registry: Unknown KW" in record.getMessage()
        for record in caplog.records
    )


def test_get_prefix_variants_handles_empty_keyword_name_and_logs_warning(caplog):
    registry = KeywordRegistry()

    caplog.set_level(logging.WARNING, logger=logger.name)

    prefixed, unprefixed = registry.get_prefix_variants("")
    assert prefixed == ""
    assert unprefixed == ""

    assert any(
        "Empty keyword_name provided to get_prefix_variants()" in record.getMessage()
        for record in caplog.records
    )


def test_get_prefix_variants_propagates_exception_and_logs_error(monkeypatch, caplog):
    registry = KeywordRegistry()

    k = _make_keyword("k1", keyword_name_without_prefix="Some KW")
    registry.register(k)

    def broken_resolve(name):
        raise RuntimeError("boom")

    monkeypatch.setattr(registry, "resolve", broken_resolve, raising=True)

    caplog.set_level(logging.ERROR, logger=logger.name)

    with pytest.raises(RuntimeError):
        registry.get_prefix_variants("Some KW")

    assert any(
        "Error while getting prefix variants for: Some KW" in record.getMessage()
        for record in caplog.records
    )


def test_get_user_defined_and_non_user_defined_keywords():
    registry = KeywordRegistry()

    k1 = _make_keyword("k1", keyword_name_without_prefix="User KW 1", is_user_defined=True)
    k2 = _make_keyword("k2", keyword_name_without_prefix="Lib KW 1", is_user_defined=False)
    k3 = _make_keyword("k3", keyword_name_without_prefix="User KW 2", is_user_defined=True)

    registry.register(k1)
    registry.register(k2)
    registry.register(k3)

    user_defined = registry.get_user_defined_keywords()
    non_user_defined = registry.get_non_user_defined_keywords()

    assert set(k.keyword_id for k in user_defined) == {"k1", "k3"}
    assert set(k.keyword_id for k in non_user_defined) == {"k2"}


def test_clear_removes_all_keywords():
    registry = KeywordRegistry()

    k1 = _make_keyword("k1")
    k2 = _make_keyword("k2")

    registry.register(k1)
    registry.register(k2)
    assert len(registry) == 2

    registry.clear()
    assert len(registry) == 0
    assert registry.get_all_keywords() == []


def test_contains_uses_resolve_true_case():
    registry = KeywordRegistry()

    k = _make_keyword("k1", keyword_name_without_prefix="Login")
    registry.register(k)

    assert "Login" in registry
    assert "Unknown" not in registry


def test_register_logs_exception_on_failure(monkeypatch, caplog):
    registry = KeywordRegistry()
    k = _make_keyword("k1", keyword_name_without_prefix="Fail KW")

    def broken_setitem(key, value):
        raise RuntimeError("boom")

    class FakeDict(dict):
        def __setitem__(self, key, value):
            broken_setitem(key, value)

    registry._keyword_registry = FakeDict()  # type: ignore[assignment]

    caplog.set_level(logging.ERROR, logger=logger.name)

    registry.register(k)

    assert len(registry) == 0
    assert any(
        "Failed to register keyword: Fail KW" in record.getMessage()
        for record in caplog.records
    )