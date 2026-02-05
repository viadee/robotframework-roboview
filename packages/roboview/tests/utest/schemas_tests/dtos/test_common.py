from pathlib import Path

from pydantic import ValidationError

from roboview.schemas.dtos.common import (
    HealthCheck,
    Shutdown,
    InitializationRequest,
    InitializationResponse,
)


def test_healthcheck_defaults_to_ok():
    hc = HealthCheck()
    assert hc.status == "OK"

    hc2 = HealthCheck(status="UP")
    assert hc2.status == "UP"


def test_shutdown_defaults_message():
    sd = Shutdown()
    assert sd.status == "Server is shutting down..."

    sd2 = Shutdown(status="Stopping now")
    assert sd2.status == "Stopping now"


def test_initialization_request_valid_with_and_without_config():
    req1 = InitializationRequest(project_root_dir=Path("/proj/root"))
    assert req1.project_root_dir == Path("/proj/root")
    assert req1.robocop_config_file is None

    req2 = InitializationRequest(
        project_root_dir=Path("/proj/root"),
        robocop_config_file=Path("/proj/robocop.toml"),
    )
    assert req2.robocop_config_file == Path("/proj/robocop.toml")


def test_initialization_request_requires_project_root_dir():
    try:
        InitializationRequest()  # type: ignore[call-arg]
    except ValidationError as exc:
        error_fields = {e["loc"][0] for e in exc.errors()}
        assert error_fields == {"project_root_dir"}


def test_initialization_response_defaults_to_ok():
    resp = InitializationResponse()
    assert resp.status == "OK"

    resp2 = InitializationResponse(status="DONE")
    assert resp2.status == "DONE"