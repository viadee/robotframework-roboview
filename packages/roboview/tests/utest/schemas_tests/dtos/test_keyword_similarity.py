from roboview.schemas.domain.keywords import KeywordUsage, SimilarKeyword
from roboview.schemas.dtos.keyword_similarity import (
    KeywordSimilarityResponse,
    DuplicateKeywordResponse,
)


def _similar(
        keyword_id: str,
        name_no_prefix: str,
        name_with_prefix: str,
        source: str,
        score: float,
) -> SimilarKeyword:
    return SimilarKeyword(
        keyword_id=keyword_id,
        keyword_name_without_prefix=name_no_prefix,
        keyword_name_with_prefix=name_with_prefix,
        source=source,
        score=score,
    )


def _usage(
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


def test_keyword_similarity_response_holds_similar_keywords():
    s1 = _similar("k1", "Login", "file.Login", "/proj/file.robot", 95.0)
    s2 = _similar("k2", "Login User", "file.Login User", "/proj/file.robot", 89.5)

    resp = KeywordSimilarityResponse(top_n_similar_keywords=[s1, s2])

    assert len(resp.top_n_similar_keywords) == 2
    ids = [s.keyword_id for s in resp.top_n_similar_keywords]
    assert ids == ["k1", "k2"]
    assert resp.top_n_similar_keywords[0].score == 95.0
    assert resp.top_n_similar_keywords[1].keyword_name_without_prefix == "Login User"


def test_duplicate_keyword_response_holds_keyword_usages():
    u1 = _usage(
        keyword_id="k1",
        file_name="a.robot",
        name_no_prefix="Login",
        name_with_prefix="a.Login",
        source="/proj/a.robot",
        file_usages=2,
        total_usages=5,
        documentation="Main login keyword",
    )
    u2 = _usage(
        keyword_id="k2",
        file_name="b.robot",
        name_no_prefix="Login User",
        name_with_prefix="b.Login User",
        source="/proj/b.robot",
        file_usages=1,
        total_usages=3,
    )

    resp = DuplicateKeywordResponse(duplicate_keywords=[u1, u2])

    assert len(resp.duplicate_keywords) == 2
    names = {u.keyword_name_without_prefix for u in resp.duplicate_keywords}
    assert names == {"Login", "Login User"}
    assert resp.duplicate_keywords[0].file_usages == 2
    assert resp.duplicate_keywords[1].file_name == "b.robot"