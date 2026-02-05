from roboview.schemas.domain.files import FileUsage
from roboview.schemas.domain.keywords import KeywordUsage
from roboview.schemas.dtos.keyword_usage import (
    InitializedKeywordsResponse,
    CalledKeywordsResponse,
    KeywordUsageResourceResponse,
    KeywordUsageRobotResponse,
    KeywordsWithoutDocResponse,
    KeywordsWithoutUsagesResponse,
)


def _kw_usage(
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


def _file_usage(file_name: str, path: str, usages: int) -> FileUsage:
    return FileUsage(file_name=file_name, path=path, usages=usages)


def test_initialized_keywords_response_holds_keyword_usages():
    k1 = _kw_usage(
        "k1",
        "a.robot",
        "Init One",
        "a.Init One",
        "/proj/a.robot",
        file_usages=1,
        total_usages=3,
    )
    k2 = _kw_usage(
        "k2",
        "b.robot",
        "Init Two",
        "b.Init Two",
        "/proj/b.robot",
        file_usages=2,
        total_usages=4,
    )

    resp = InitializedKeywordsResponse(initialized_keywords=[k1, k2])

    assert len(resp.initialized_keywords) == 2
    ids = [k.keyword_id for k in resp.initialized_keywords]
    assert ids == ["k1", "k2"]


def test_called_keywords_response_holds_keyword_usages():
    k1 = _kw_usage(
        "k1",
        "a.robot",
        "Call One",
        "a.Call One",
        "/proj/a.robot",
        file_usages=5,
        total_usages=10,
    )

    resp = CalledKeywordsResponse(called_keywords=[k1])

    assert len(resp.called_keywords) == 1
    assert resp.called_keywords[0].keyword_name_without_prefix == "Call One"
    assert resp.called_keywords[0].file_usages == 5


def test_keyword_usage_resource_response_holds_file_usages():
    f1 = _file_usage("res1.resource", "/proj/res1.resource", usages=2)
    f2 = _file_usage("res2.resource", "/proj/res2.resource", usages=1)

    resp = KeywordUsageResourceResponse(keyword_usage_resource=[f1, f2])

    assert len(resp.keyword_usage_resource) == 2
    names = {f.file_name for f in resp.keyword_usage_resource}
    assert names == {"res1.resource", "res2.resource"}


def test_keyword_usage_robot_response_holds_file_usages():
    f1 = _file_usage("suite1.robot", "/proj/suite1.robot", usages=3)

    resp = KeywordUsageRobotResponse(keyword_usage_robot=[f1])

    assert len(resp.keyword_usage_robot) == 1
    assert resp.keyword_usage_robot[0].path == "/proj/suite1.robot"
    assert resp.keyword_usage_robot[0].usages == 3


def test_keywords_without_doc_response_holds_keyword_usages():
    k1 = _kw_usage(
        "k1",
        "a.robot",
        "No Doc",
        "a.No Doc",
        "/proj/a.robot",
        file_usages=0,
        total_usages=0,
        documentation=None,
    )

    resp = KeywordsWithoutDocResponse(keywords_wo_documentation=[k1])

    assert len(resp.keywords_wo_documentation) == 1
    assert resp.keywords_wo_documentation[0].documentation is None
    assert resp.keywords_wo_documentation[0].keyword_name_without_prefix == "No Doc"


def test_keywords_without_usages_response_holds_keyword_usages():
    k1 = _kw_usage(
        "k1",
        "a.robot",
        "Unused",
        "a.Unused",
        "/proj/a.robot",
        file_usages=0,
        total_usages=0,
    )
    k2 = _kw_usage(
        "k2",
        "b.robot",
        "Also Unused",
        "b.Also Unused",
        "/proj/b.robot",
        file_usages=0,
        total_usages=0,
    )

    resp = KeywordsWithoutUsagesResponse(keywords_wo_usages=[k1, k2])

    assert len(resp.keywords_wo_usages) == 2
    assert all(k.total_usages == 0 for k in resp.keywords_wo_usages)