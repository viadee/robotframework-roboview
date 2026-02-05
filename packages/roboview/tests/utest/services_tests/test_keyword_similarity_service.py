import logging
from typing import Iterable

import numpy as np
import pytest
from pygments.lexers import get_lexer_by_name

from roboview.registries.keyword_registry import KeywordRegistry
from roboview.schemas.domain.keywords import KeywordProperties, SimilarKeyword
from roboview.services.keyword_similarity_service import (
    KeywordSimilarityService,
    logger,
)


def _kw(
        keyword_id: str,
        name_no_prefix: str,
        name_with_prefix: str,
        code: str,
        source: str = "/proj/file.robot",
        is_user_defined: bool = True,
) -> KeywordProperties:
    base_no = name_no_prefix.lower().replace(" ", "").replace("_", "")
    base_with = name_with_prefix.lower().replace(" ", "").replace("_", "")
    return KeywordProperties(
        keyword_id=keyword_id,
        file_name=source.split("/")[-1],
        keyword_name_without_prefix=name_no_prefix,
        keyword_name_with_prefix=name_with_prefix,
        description=None,
        is_user_defined=is_user_defined,
        code=code,
        source=source,
        validation_str_without_prefix=base_no,
        validation_str_with_prefix=base_with,
    )


class FakeKeywordRegistry(KeywordRegistry):
    """Thin wrapper so we can easily inject predefined keywords."""

    def __init__(self, keywords: list[KeywordProperties] | None = None) -> None:
        super().__init__()
        if keywords:
            for k in keywords:
                self.register(k)


def test_calculate_similarity_matrix_no_user_keywords_logs_warning_and_does_nothing(caplog):
    reg = FakeKeywordRegistry(keywords=[])
    svc = KeywordSimilarityService(reg)

    caplog.set_level(logging.WARNING, logger=logger.name)

    svc.calculate_keyword_similarity_matrix()

    assert svc.similarity_matrix.size == 0
    assert svc.keyword_names_list == []
    assert any(
        "No keywords found. Similarity matrix cannot be computed." in r.getMessage()
        for r in caplog.records
    )


def test_calculate_similarity_matrix_builds_matrix_and_names(monkeypatch):
    kws = [
        _kw("k1", "KW One", "file.KW One", "KW One\n    Log    Hello"),
        _kw("k2", "KW Two", "file.KW Two", "KW Two\n    Log    World"),
    ]
    reg = FakeKeywordRegistry(kws)
    svc = KeywordSimilarityService(reg)

    monkeypatch.setattr(
        "roboview.services.keyword_similarity_service.get_lexer_by_name",
        lambda name: get_lexer_by_name("text"),
        raising=True,
    )

    svc.calculate_keyword_similarity_matrix()

    assert svc.similarity_matrix.shape == (2, 2)
    assert svc.keyword_names_list == ["file.KW One", "file.KW Two"]
    assert pytest.approx(svc.similarity_matrix[0, 0], rel=1e-5) == 1.0
    assert pytest.approx(svc.similarity_matrix[1, 1], rel=1e-5) == 1.0


def test_calculate_similarity_matrix_logs_and_returns_when_lexer_init_fails(monkeypatch, caplog):
    kws = [
        _kw("k1", "KW", "file.KW", "KW\n    Log    Something"),
    ]
    reg = FakeKeywordRegistry(kws)
    svc = KeywordSimilarityService(reg)

    def broken_get_lexer(name: str):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        "roboview.services.keyword_similarity_service.get_lexer_by_name",
        broken_get_lexer,
        raising=True,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    svc.calculate_keyword_similarity_matrix()

    assert svc.similarity_matrix.size == 0
    assert any(
        "Failed to initialize lexer or tokenize keywords" in r.getMessage()
        for r in caplog.records
    )


def test_calculate_similarity_matrix_logs_and_returns_when_vectorizer_fails(monkeypatch, caplog):
    kws = [
        _kw("k1", "KW One", "file.KW One", "KW One\n    Log    Hello"),
        _kw("k2", "KW Two", "file.KW Two", "KW Two\n    Log    World"),
    ]
    reg = FakeKeywordRegistry(kws)
    svc = KeywordSimilarityService(reg)

    monkeypatch.setattr(
        "roboview.services.keyword_similarity_service.get_lexer_by_name",
        lambda name: get_lexer_by_name("text"),
        raising=True,
    )

    class BrokenVectorizer:
        def fit_transform(self, docs: Iterable[str]):
            raise RuntimeError("boom")

    monkeypatch.setattr(
        "roboview.services.keyword_similarity_service.CountVectorizer",
        BrokenVectorizer,
        raising=True,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    svc.calculate_keyword_similarity_matrix()

    assert svc.similarity_matrix.size == 0
    assert any(
        "Failed to create vectors or calculate similarity matrix" in r.getMessage()
        for r in caplog.records
    )


def test_get_n_most_similar_keywords_empty_keyword_logs_warning_and_returns_empty(caplog):
    reg = FakeKeywordRegistry([])
    svc = KeywordSimilarityService(reg)

    caplog.set_level(logging.WARNING, logger=logger.name)

    result = svc.get_n_most_similar_keywords("", top_n=3)
    assert result == []
    assert any(
        "Empty keyword provided to get_n_most_similar_keywords" in r.getMessage()
        for r in caplog.records
    )


def test_get_n_most_similar_keywords_keyword_not_in_registry_logs_warning_and_returns_empty(caplog):
    reg = FakeKeywordRegistry([])
    svc = KeywordSimilarityService(reg)

    caplog.set_level(logging.WARNING, logger=logger.name)

    result = svc.get_n_most_similar_keywords("Some KW", top_n=3)
    assert result == []
    assert any(
        "Keyword not found in similarity matrix" in r.getMessage()
        for r in caplog.records
    )


def test_get_n_most_similar_keywords_keyword_not_in_keyword_names_list_logs_warning_and_returns_empty(monkeypatch, caplog):
    kws = [
        _kw("k1", "KW One", "file.KW One", "KW One\n    Log    Hello"),
    ]
    reg = FakeKeywordRegistry(kws)
    svc = KeywordSimilarityService(reg)

    svc.similarity_matrix = np.array([[1.0]])
    svc.keyword_names_list = ["some.other.Name"]

    caplog.set_level(logging.WARNING, logger=logger.name)

    result = svc.get_n_most_similar_keywords("file.KW One", top_n=3)
    assert result == []
    assert any(
        "Keyword 'file.KW One' not found in keyword list" in r.getMessage()
        for r in caplog.records
    )


def test_get_n_most_similar_keywords_happy_path(monkeypatch):
    kws = [
        _kw("k1", "KW One", "file.KW One", "code1"),
        _kw("k2", "KW Two", "file.KW Two", "code2"),
        _kw("k3", "KW Three", "file.KW Three", "code3"),
    ]
    reg = FakeKeywordRegistry(kws)
    svc = KeywordSimilarityService(reg)

    svc.keyword_names_list = ["file.KW One", "file.KW Two", "file.KW Three"]
    svc.similarity_matrix = np.array(
        [
            [1.0, 0.9, 0.1],
            [0.9, 1.0, 0.2],
            [0.1, 0.2, 1.0],
        ]
    )

    result = svc.get_n_most_similar_keywords("file.KW One", top_n=2)

    assert len(result) == 2
    assert all(isinstance(r, SimilarKeyword) for r in result)
    assert [r.keyword_name_with_prefix for r in result] == [
        "file.KW Two",
        "file.KW Three",
    ]
    assert result[0].score == 0.9
    assert result[1].score == 0.1


def test_get_n_most_similar_keywords_handles_invalid_index_and_continues(caplog):
    kws = [
        _kw("k1", "KW One", "file.KW One", "code1"),
        _kw("k2", "KW Two", "file.KW Two", "code2"),
    ]
    reg = FakeKeywordRegistry(kws)
    svc = KeywordSimilarityService(reg)

    svc.keyword_names_list = ["file.KW One"]
    svc.similarity_matrix = np.array([[1.0, 0.5], [0.5, 1.0]])

    caplog.set_level(logging.ERROR, logger=logger.name)

    result = svc.get_n_most_similar_keywords("file.KW One", top_n=1)

    assert result == []
    assert any(
        "Invalid index or similarity score at position" in r.getMessage()
        for r in caplog.records
    )


def test_get_all_similar_keywords_above_threshold_empty_matrix_logs_warning_and_returns_empty(caplog):
    reg = FakeKeywordRegistry([])
    svc = KeywordSimilarityService(reg)

    caplog.set_level(logging.WARNING, logger=logger.name)

    result = svc.get_all_similar_keywords_above_threshold(0.8)
    assert result == []
    assert any(
        "Similarity matrix is empty" in r.getMessage()
        for r in caplog.records
    )


def test_get_all_similar_keywords_above_threshold_happy_path():
    kws = [
        _kw("k1", "KW One", "file.KW One", "code1"),
        _kw("k2", "KW Two", "file.KW Two", "code2"),
        _kw("k3", "KW Three", "file.KW Three", "code3"),
    ]
    reg = FakeKeywordRegistry(kws)
    svc = KeywordSimilarityService(reg)

    svc.keyword_names_list = ["file.KW One", "file.KW Two", "file.KW Three"]
    svc.similarity_matrix = np.array(
        [
            [1.0, 0.85, 0.2],
            [0.85, 1.0, 0.3],
            [0.2, 0.3, 1.0],
        ]
    )

    result = svc.get_all_similar_keywords_above_threshold(threshold=0.8)

    assert len(result) == 2
    names = {k.keyword_name_with_prefix for k in result}
    assert names == {"file.KW One", "file.KW Two"}


def test_get_all_similar_keywords_above_threshold_handles_resolve_errors(monkeypatch, caplog):
    kws = [
        _kw("k1", "KW One", "file.KW One", "code1"),
        _kw("k2", "KW Two", "file.KW Two", "code2"),
    ]
    reg = FakeKeywordRegistry(kws)
    svc = KeywordSimilarityService(reg)

    svc.keyword_names_list = ["file.KW One", "file.KW Two"]
    svc.similarity_matrix = np.array([[1.0, 0.9], [0.9, 1.0]])

    def broken_resolve(name: str):
        raise RuntimeError("boom")

    monkeypatch.setattr(
        reg,
        "resolve",
        broken_resolve,
        raising=True,
    )

    caplog.set_level(logging.ERROR, logger=logger.name)

    result = svc.get_all_similar_keywords_above_threshold(threshold=0.5)

    assert result == []
    assert any(
        "Unexpected error while finding similar keywords" in r.getMessage()
        for r in caplog.records
    )