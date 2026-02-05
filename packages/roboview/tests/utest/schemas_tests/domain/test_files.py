from pydantic import ValidationError

from roboview.schemas.domain.files import FileProperties, FileUsage, SelectionFiles


def test_file_properties_minimal_valid():
    f = FileProperties(
        file_name="test.robot",
        path="/proj/test.robot",
        is_resource=False,
    )

    assert f.file_name == "test.robot"
    assert f.path == "/proj/test.robot"
    assert f.is_resource is False
    assert f.initialized_keywords is None
    assert f.called_keywords is None
    assert f.imported_files is None


def test_file_properties_full_valid():
    f = FileProperties(
        file_name="res.resource",
        path="/proj/res.resource",
        is_resource=True,
        initialized_keywords=["Init 1", "Init 2"],
        called_keywords=["Call 1"],
        imported_files=["common.resource", "Library    SeleniumLibrary"],
    )

    assert f.is_resource is True
    assert f.initialized_keywords == ["Init 1", "Init 2"]
    assert f.called_keywords == ["Call 1"]
    assert f.imported_files == ["common.resource", "Library    SeleniumLibrary"]


def test_file_properties_requires_mandatory_fields():
    try:
        FileProperties()  # type: ignore[call-arg]
    except ValidationError as exc:
        error_fields = {e["loc"][0] for e in exc.errors()}
        assert "file_name" in error_fields
        assert "path" in error_fields
        assert "is_resource" in error_fields


def test_file_usage_valid():
    u = FileUsage(
        file_name="suite.robot",
        path="/proj/suite.robot",
        usages=3,
    )

    assert u.file_name == "suite.robot"
    assert u.path == "/proj/suite.robot"
    assert u.usages == 3


def test_file_usage_requires_all_fields():
    try:
        FileUsage()  # type: ignore[call-arg]
    except ValidationError as exc:
        error_fields = {e["loc"][0] for e in exc.errors()}
        assert error_fields == {"file_name", "path", "usages"}


def test_selection_files_valid():
    s = SelectionFiles(
        file_name="select.robot",
        path="/proj/select.robot",
    )

    assert s.file_name == "select.robot"
    assert s.path == "/proj/select.robot"


def test_selection_files_requires_all_fields():
    try:
        SelectionFiles()  # type: ignore[call-arg]
    except ValidationError as exc:
        error_fields = {e["loc"][0] for e in exc.errors()}
        assert error_fields == {"file_name", "path"}