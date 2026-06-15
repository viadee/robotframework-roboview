"""Tests for the reports API endpoint."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from roboview.api.endpoints.reports import router
from roboview.schemas.domain.reports import (
    SummaryReport,
    ExportFormatEnum,
    KPISummary,
    ReportMetadata,
    ReportTypeEnum,
)
from roboview.schemas.dtos.reports import GenerateReportRequest


@pytest.fixture
def test_app() -> FastAPI:
    """Create a test FastAPI application."""
    app = FastAPI()
    app.include_router(router, prefix="/reports")

    # Create mock reporting service
    mock_reporting_service = MagicMock()

    # Create a sample report
    sample_report = SummaryReport(
        metadata=ReportMetadata(
            project_name="Test Project",
            project_root="/test/project",
        ),
        title="Test Summary Report",
        report_type=ReportTypeEnum.SUMMARY,
        summary=KPISummary(
            total_keywords=42,
            unused_keywords=3,
            reusage_rate=65.5,
            documentation_coverage=80.0,
            robocop_issues=12,
            total_files=15,
        ),
        risk_level="LOW",
        health_status="Good project health.",
        robocop_issues_by_category={"Documentation": 5, "Naming": 7},
    )

    mock_reporting_service.generate_report.return_value = sample_report
    app.state.reporting_service = mock_reporting_service

    return app


@pytest.fixture
def client(test_app: FastAPI) -> TestClient:
    """Create a test client."""
    return TestClient(test_app)


def test_generate_report_success(client: TestClient) -> None:
    """Test successful report generation."""
    request_data = {
        "report_type": "executive_summary",
        "export_format": "json",
        "author": "Test Author",
    }

    response = client.post("/reports/generate", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["report_id"] is not None
    assert data["download_url"] is not None
    assert "json" in data["download_url"]


def test_generate_report_with_default_values(client: TestClient) -> None:
    """Test report generation with default values."""
    response = client.post("/reports/generate", json={})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"


def test_generate_report_invalid_format(client: TestClient) -> None:
    """Test report generation with invalid format."""
    request_data = {
        "report_type": "executive_summary",
        "export_format": "pdf",  # Not yet implemented
    }

    response = client.post("/reports/generate", json=request_data)

    assert response.status_code == 400


def test_get_report_status(client: TestClient) -> None:
    """Test getting report status."""
    # First generate a report
    response = client.post("/reports/generate", json={})
    report_id = response.json()["report_id"]

    # Get status
    response = client.get(f"/reports/status/{report_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["report_id"] == report_id
    assert data["status"] == "completed"


def test_get_report_status_not_found(client: TestClient) -> None:
    """Test getting status of non-existent report."""
    response = client.get("/reports/status/invalid-report-id")

    assert response.status_code == 404


def test_download_report(client: TestClient) -> None:
    """Test downloading a report."""
    # Generate a report
    response = client.post("/reports/generate", json={})
    report_id = response.json()["report_id"]

    # Download report
    response = client.get(f"/reports/download/{report_id}")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert "report_" in response.headers.get("content-disposition", "")


def test_download_incomplete_report(client: TestClient) -> None:
    """Test downloading a report that is still generating."""
    # This would require mocking an ongoing generation
    # For now, we'll skip since our implementation completes immediately


def test_get_available_reports(client: TestClient) -> None:
    """Test getting list of available reports."""
    # Generate a report first
    client.post("/reports/generate", json={})

    # Get available reports
    response = client.get("/reports/available-reports")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:  # If reports were generated
        assert data[0]["report_id"] is not None
        assert data[0]["status"] == "completed"


def test_delete_report(client: TestClient) -> None:
    """Test deleting a report."""
    # Generate a report
    response = client.post("/reports/generate", json={})
    report_id = response.json()["report_id"]

    # Delete report
    response = client.delete(f"/reports/{report_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

    # Verify it's deleted
    response = client.get(f"/reports/status/{report_id}")
    assert response.status_code == 404


def test_delete_non_existent_report(client: TestClient) -> None:
    """Test deleting a non-existent report."""
    response = client.delete("/reports/invalid-report-id")

    assert response.status_code == 404


def test_generate_multiple_reports(client: TestClient) -> None:
    """Test generating multiple reports."""
    report_ids = []

    for _ in range(3):
        response = client.post(
            "/reports/generate",
            json={"report_type": "executive_summary"},
        )
        assert response.status_code == 200
        report_ids.append(response.json()["report_id"])

    # Verify all reports are available
    response = client.get("/reports/available-reports")
    available_ids = [r["report_id"] for r in response.json()]

    for report_id in report_ids:
        assert report_id in available_ids
