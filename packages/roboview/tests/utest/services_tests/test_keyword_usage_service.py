import logging
from pathlib import Path

from roboview.registries.file_registry import FileRegistry
from roboview.registries.keyword_registry import KeywordRegistry
from roboview.schemas.domain.common import FileType, KeywordType
from roboview.schemas.domain.files import FileProperties
from roboview.schemas.domain.keywords import KeywordProperties, KeywordUsage
from roboview.services.keyword_similarity_service import KeywordSimilarityService
from roboview.services.keyword_usage_service import KeywordUsageService, logger


def _file(
        file_name: str,
        path: str,
        is_resource: bool = False,
        initialized_keywords: list[str] | None = None,
        called_keywords: list[str] | None = None,
) -> FileProperties:
    return FileProperties(
        file_name=file_name,
        path=path,
        is_resource=is_resource,
        initialized_keywords=initialized_keywords or [],
        called_keywords=called_keywords or [],
        imported_files=[],
    )


def _kw(
        keyword_id: str,
        name_no_prefix: str,
        name_with_prefix: str,
        description: str | None = None,
        code: str = "",
        source: str = "/proj/file.robot",
        is_user_defined: bool = True,
) -> KeywordProperties:
    base_no = name_no_prefix.lower().replace(" ", "").replace("_", "")
    base_with = name_with_prefix.lower().replace(" ", "").replace("_", "")
    return KeywordProperties(
        keyword_id=keyword_id,
        file_name=Path(source).name,
        keyword_name_without_prefix=name_no_prefix,
        keyword_name_with_prefix=name_with_prefix,
        description=description,
        is_user_defined=is_user_defined,
        code=code,
        source=source,
        validation_str_without_prefix=base_no,
        validation_str_with_prefix=base_with,
    )


def _make_registries(
        files: list[FileProperties],
        keywords: list[KeywordProperties],
) -> tuple[KeywordRegistry, FileRegistry]:
    kreg = KeywordRegistry()
    freg = FileRegistry()

    for k in keywords:
        kreg.register(k)

    for f in files:
        freg.register(f)

    return kreg, freg


def test_get_keywords_with_global_usage_for_file_initialized_and_called(tmp_path):
    f1 = _file(
        "suite.robot",
        "/proj/suite.robot",
        initialized_keywords=["Login User"],
        called_keywords=["Login User", "Helper KW"],
    )

    kw1 = _kw(
        "k1",
        "Login User",
        "suite.Login User",
        description="Logs user in",
        source="/proj/suite.robot",
    )

    kw2 = _kw(
        "k2",
        "Helper KW",
        "suite.Helper KW",
        description="Helper",
        source="/proj/suite.robot",
    )

    kreg, freg = _make_registries([f1], [kw1, kw2])
    svc = KeywordUsageService(kreg, freg)

    res_init = svc.get_keywords_with_global_usage_for_file(
        Path("/proj/suite.robot"),
        KeywordType.INITIALIZED,
    )

    assert len(res_init) == 1
    r = res_init[0]
    assert isinstance(r, KeywordUsage)
    assert r.keyword_id == "k1"
    assert r.file_usages == 1
    assert r.total_usages == 1

    res_called = svc.get_keywords_with_global_usage_for_file(
        Path("/proj/suite.robot"),
        KeywordType.CALLED,
    )

    ids = {k.keyword_id for k in res_called}
    assert ids == {"k1", "k2"}


def test_get_keyword_usage_in_files_for_target_keyword_resource_vs_robot():
    f_res = _file(
        "common.resource",
        "/proj/common.resource",
        is_resource=True,
        called_keywords=["Do Thing", "Do Thing"],
    )

    f_robot = _file(
        "suite.robot",
        "/proj/suite.robot",
        is_resource=False,
        called_keywords=["Do Thing"],
    )

    kw = _kw("k1", "Do Thing", "common.Do Thing")

    kreg, freg = _make_registries([f_res, f_robot], [kw])
    svc = KeywordUsageService(kreg, freg)

    res_resource = svc.get_keyword_usage_in_files_for_target_keyword("Do Thing", FileType.RESOURCE)

    assert len(res_resource) == 1
    assert res_resource[0].file_name == "common.resource"
    assert res_resource[0].usages == 2

    res_robot = svc.get_keyword_usage_in_files_for_target_keyword("Do Thing", FileType.ROBOT)

    assert len(res_robot) == 1
    assert res_robot[0].file_name == "suite.robot"
    assert res_robot[0].usages == 1


def test_get_keyword_usage_in_files_for_target_keyword_missing_keyword_logs_warning_and_returns_empty(caplog):
    kreg, freg = _make_registries([], [])
    svc = KeywordUsageService(kreg, freg)

    caplog.set_level(logging.WARNING, logger=logger.name)

    res = svc.get_keyword_usage_in_files_for_target_keyword("Unknown", FileType.ROBOT)

    assert res == []

    assert any(
        "Keyword 'Unknown' not found in registry" in r.getMessage()
        for r in caplog.records
    )


def test_get_keywords_without_documentation_and_usages():
    kw1 = _kw("k1", "With Doc", "file.With Doc", description="Has doc")
    kw2 = _kw("k2", "No Doc", "file.No Doc", description=None)
    kw_lib = _kw("k3", "Lib KW", "Lib.Lib KW", description="Lib", is_user_defined=False)

    f1 = _file(
        "file.robot",
        "/proj/file.robot",
        called_keywords=["file.With Doc", "file.With Doc"],
    )

    kreg, freg = _make_registries([f1], [kw1, kw2, kw_lib])
    svc = KeywordUsageService(kreg, freg)

    without_doc = svc.get_keywords_without_documentation()

    assert {k.keyword_id for k in without_doc} == {"k2"}
    assert without_doc[0].keyword_name_without_prefix == "No Doc"
    assert without_doc[0].total_usages == 0

    without_usages = svc.get_keywords_without_usages()

    assert {k.keyword_id for k in without_usages} == {"k2"}


class FakeKeywordSimService(KeywordSimilarityService):
    def __init__(self, keywords_to_return):
        super().__init__(KeywordRegistry())
        self._keywords_to_return = keywords_to_return

    def get_all_similar_keywords_above_threshold(self, threshold: float = 0.80):
        return self._keywords_to_return


def test_get_potential_duplicate_keywords_uses_similarity_service():
    kw1 = _kw("k1", "KW One", "file.KW One", description=None, source="/proj/file.robot")
    kw2 = _kw("k2", "KW Two", "file.KW Two", description=None, source="/proj/other.robot")

    f1 = _file(
        "file.robot",
        "/proj/file.robot",
        called_keywords=["file.KW One", "file.KW Two"],
    )

    f2 = _file(
        "other.robot",
        "/proj/other.robot",
        called_keywords=["file.KW Two"],
    )

    kreg, freg = _make_registries([f1, f2], [kw1, kw2])
    svc = KeywordUsageService(kreg, freg)

    sim_svc = FakeKeywordSimService([kw1, kw2])

    res = svc.get_potential_duplicate_keywords(sim_svc)

    assert len(res) == 2

    by_id = {k.keyword_id: k for k in res}
    assert by_id["k1"].total_usages == 1
    assert by_id["k2"].total_usages == 2


def test_get_keyword_reusage_rate_and_doc_coverage():
    kw1 = _kw("k1", "User1", "file.User1", description="Doc1")
    kw2 = _kw("k2", "User2", "file.User2", description=None)
    kw3 = _kw("k3", "User3", "file.User3", description="Doc3")
    kw_ext = _kw("k4", "Lib KW", "Lib.Lib KW", description="Lib", is_user_defined=False)

    f1 = _file(
        "a.robot",
        "/proj/a.robot",
        called_keywords=["file.User1", "file.User1", "file.User2"],
    )

    f2 = _file(
        "b.robot",
        "/proj/b.robot",
        called_keywords=["file.User1"],
    )

    kreg, freg = _make_registries([f1, f2], [kw1, kw2, kw3, kw_ext])
    svc = KeywordUsageService(kreg, freg)

    reusage = svc.get_keyword_reusage_rate()
    assert reusage == 0.33

    doc_cov = svc.get_documentation_coverage()
    assert doc_cov == 0.67


def test_get_keyword_reusage_rate_no_user_keywords_logs_warning_and_returns_0(caplog):
    kreg, freg = _make_registries([], [])
    svc = KeywordUsageService(kreg, freg)

    caplog.set_level(logging.WARNING, logger=logger.name)

    rate = svc.get_keyword_reusage_rate()

    assert rate == 0.0

    assert any(
        "No user-defined keywords found for reusage rate calculation" in r.getMessage()
        for r in caplog.records
    )


def test_get_documentation_coverage_no_user_keywords_logs_warning_and_returns_0(caplog):
    kw = _kw("k1", "Lib KW", "Lib.Lib KW", description=None, is_user_defined=False)

    kreg, freg = _make_registries([], [kw])
    svc = KeywordUsageService(kreg, freg)

    caplog.set_level(logging.WARNING, logger=logger.name)

    cov = svc.get_documentation_coverage()

    assert cov == 0.0

    assert any(
        "No user-defined keywords found for documentation coverage calculation" in r.getMessage()
        for r in caplog.records
    )


def test_get_most_used_user_defined_and_external_keywords():
    kw1 = _kw("k1", "User1", "file.User1", description=None)
    kw2 = _kw("k2", "User2", "file.User2", description=None)
    kw_ext1 = _kw("k3", "Lib1", "Lib.Lib1", description=None, is_user_defined=False)
    kw_ext2 = _kw("k4", "Lib2", "Lib.Lib2", description=None, is_user_defined=False)

    f1 = _file(
        "a.robot",
        "/proj/a.robot",
        called_keywords=["file.User1", "file.User1", "file.User2", "Lib.Lib1"],
    )

    f2 = _file(
        "b.robot",
        "/proj/b.robot",
        called_keywords=["file.User2", "Lib.Lib1", "Lib.Lib2", "Lib.Lib2"],
    )

    kreg, freg = _make_registries([f1, f2], [kw1, kw2, kw_ext1, kw_ext2])
    svc = KeywordUsageService(kreg, freg)

    top_users = svc.get_most_used_user_defined_keywords(top_n=2)
    assert [k.keyword_name_with_prefix for k in top_users] == ["file.User1", "file.User2"]

    top_ext = svc.get_most_used_external_or_builtin_keywords(top_n=2)
    ext_names = {k.keyword_name_with_prefix for k in top_ext}
    assert ext_names == {"Lib.Lib2", "Lib.Lib1"}


def test__get_init_and_called_keywords_for_file():
    f1 = _file(
        "suite.robot",
        "/proj/suite.robot",
        initialized_keywords=["Init1"],
        called_keywords=["Call1"],
    )

    f2 = _file(
        "other.robot",
        "/proj/other.robot",
        initialized_keywords=["Init2"],
        called_keywords=["Call2"],
    )

    kreg, freg = _make_registries([f1, f2], [])
    svc = KeywordUsageService(kreg, freg)

    inits = svc._get_init_keywords_for_file("/proj/suite.robot")
    calls = svc._get_called_keywords_for_file("/proj/other.robot")

    assert inits == ["Init1"]
    assert calls == ["Call2"]


def test__get_keyword_usage_for_target_keyword_in_file_and_global_usage():
    f1 = _file(
        "a.robot",
        "/proj/a.robot",
        called_keywords=["file.KW", "KW"],
    )

    f2 = _file(
        "b.robot",
        "/proj/b.robot",
        called_keywords=["KW", "Something"],
    )

    kw = _kw("k1", "KW", "file.KW")

    kreg, freg = _make_registries([f1, f2], [kw])
    svc = KeywordUsageService(kreg, freg)

    per_file = svc._get_keyword_usage_for_target_keyword_in_file("file.KW", "/proj/a.robot")
    assert per_file == 2

    total = svc._get_global_keyword_usage_for_target_keyword("file.KW")
    assert total == 3