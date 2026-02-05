from roboview.schemas.domain.files import SelectionFiles
from roboview.schemas.dtos.files import (
    ResourceFilesResponse,
    RobotFilesResponse,
    AllFilesResponse,
)


def _sel(file_name: str, path: str) -> SelectionFiles:
    return SelectionFiles(file_name=file_name, path=path)


def test_resource_files_response_holds_selection_files_list():
    files = [
        _sel("res1.resource", "/proj/res1.resource"),
        _sel("res2.resource", "/proj/res2.resource"),
    ]

    resp = ResourceFilesResponse(resource_files=files)

    assert len(resp.resource_files) == 2
    assert resp.resource_files[0].file_name == "res1.resource"
    assert resp.resource_files[1].path == "/proj/res2.resource"


def test_robot_files_response_holds_selection_files_list():
    files = [
        _sel("suite1.robot", "/proj/suite1.robot"),
        _sel("suite2.robot", "/proj/suite2.robot"),
    ]

    resp = RobotFilesResponse(robot_files=files)

    assert len(resp.robot_files) == 2
    assert {f.file_name for f in resp.robot_files} == {"suite1.robot", "suite2.robot"}


def test_all_files_response_holds_selection_files_list():
    files = [
        _sel("suite1.robot", "/proj/suite1.robot"),
        _sel("res1.resource", "/proj/res1.resource"),
    ]

    resp = AllFilesResponse(all_files=files)

    assert len(resp.all_files) == 2
    assert {(f.file_name, f.path) for f in resp.all_files} == {
        ("suite1.robot", "/proj/suite1.robot"),
        ("res1.resource", "/proj/res1.resource"),
    }