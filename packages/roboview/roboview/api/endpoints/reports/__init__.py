"""Endpoints for report generation and management."""

import logging
import tempfile
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from roboview.schemas.dtos.reports import GenerateReportRequest, ReportStatusResponse
from roboview.utils.exporters.html_exporter import HTMLExporter
from starlette.requests import Request
from starlette.responses import FileResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory store for report status (in production, would use database)
_REPORT_STATUS_STORE: dict[str, dict] = {}


@router.post(
    "/generate",
    summary="Generate a summary report",
    response_model=ReportStatusResponse,
    responses={
        200: {"description": "Report generation started."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
    },
)
async def generate_report(request: Request, report_request: GenerateReportRequest):  # noqa: ANN201
    """Generate a comprehensive summary report as HTML.

    Arguments:
        request: FastAPI request object
        report_request: Report generation request

    Returns:
        ReportStatusResponse: Status of report generation

    """
    try:
        report_id = str(uuid4())
        created_at = datetime.utcnow().isoformat()

        # Store report status
        _REPORT_STATUS_STORE[report_id] = {
            "status": "generating",
            "created_at": created_at,
            "report_type": "summary",
            "export_format": "html",
        }

        # Generate summary report
        reporting_service = request.app.state.reporting_service
        report = reporting_service.generate_report(author=report_request.author)

        # Export to HTML
        temp_dir = Path(tempfile.gettempdir()) / ".roboview" / "reports"
        temp_dir.mkdir(parents=True, exist_ok=True)

        output_file = temp_dir / f"{report_id}.html"
        HTMLExporter.export(report, output_file)
        file_size = output_file.stat().st_size

        # Update status
        _REPORT_STATUS_STORE[report_id] = {
            "status": "completed",
            "created_at": created_at,
            "report_type": "summary",
            "export_format": "html",
            "file_path": str(output_file),
            "file_size": file_size,
        }

        return ReportStatusResponse(
            report_id=report_id,
            status="completed",
            download_url=f"/v1/reports/download/{report_id}",
            file_size=file_size,
            created_at=created_at,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error generating report: %s", e)
        report_id_local = str(uuid4())
        _REPORT_STATUS_STORE[report_id_local] = {
            "status": "failed",
            "error": str(e),
        }
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


@router.get(
    "/status/{report_id}",
    summary="Get report generation status",
    response_model=ReportStatusResponse,
    responses={
        200: {"description": "Report status retrieved."},
        404: {"description": "Report not found."},
        500: {"description": "Internal Server Error."},
    },
)
async def get_report_status(report_id: str):  # noqa: ANN201
    """Get the status of a report generation request.

    Arguments:
        report_id: ID of the report

    Returns:
        ReportStatusResponse: Status of the report

    """
    try:
        if report_id not in _REPORT_STATUS_STORE:
            raise HTTPException(status_code=404, detail="Report not found")

        status_data = _REPORT_STATUS_STORE[report_id]
        return ReportStatusResponse(
            report_id=report_id,
            status=status_data["status"],
            download_url=f"/v1/reports/download/{report_id}" if status_data["status"] == "completed" else None,
            error_message=status_data.get("error"),
            file_size=status_data.get("file_size"),
            created_at=status_data["created_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error retrieving report status: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


@router.get(
    "/download/{report_id}",
    summary="Download a generated report",
    responses={
        200: {"description": "Report file downloaded."},
        404: {"description": "Report not found."},
        500: {"description": "Internal Server Error."},
    },
)
async def download_report(report_id: str):  # noqa: ANN201
    """Download a generated report file.

    Arguments:
        report_id: ID of the report

    Returns:
        FileResponse: Report file

    """
    try:
        if report_id not in _REPORT_STATUS_STORE:
            raise HTTPException(status_code=404, detail="Report not found")

        status_data = _REPORT_STATUS_STORE[report_id]
        if status_data["status"] != "completed":
            raise HTTPException(status_code=400, detail="Report generation not completed")

        file_path = Path(status_data["file_path"])
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Report file not found")

        # Determine media type based on format
        export_format = status_data["export_format"]
        media_type = "text/html"

        return FileResponse(
            file_path,
            media_type=media_type,
            filename=f"report_{report_id[:8]}.html",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error downloading report: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


@router.get(
    "/available-reports",
    summary="Get list of available reports",
    responses={
        200: {"description": "List of reports retrieved."},
        500: {"description": "Internal Server Error."},
    },
)
async def get_available_reports():  # noqa: ANN201
    """Get list of available reports.

    Returns:
        List of report metadata

    """
    try:
        reports = []
        for report_id, status_data in _REPORT_STATUS_STORE.items():
            if status_data["status"] == "completed":
                reports.append(
                    {
                        "report_id": report_id,
                        "report_type": status_data["report_type"],
                        "export_format": status_data["export_format"],
                        "created_at": status_data["created_at"],
                        "file_size": status_data.get("file_size"),
                        "status": status_data["status"],
                    }
                )

        return reports

    except Exception as e:
        logger.exception("Error retrieving available reports: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e


@router.delete(
    "/{report_id}",
    summary="Delete a generated report",
    responses={
        200: {"description": "Report deleted."},
        404: {"description": "Report not found."},
        500: {"description": "Internal Server Error."},
    },
)
async def delete_report(report_id: str):  # noqa: ANN201
    """Delete a generated report.

    Arguments:
        report_id: ID of the report to delete

    Returns:
        Success message

    """
    try:
        if report_id not in _REPORT_STATUS_STORE:
            raise HTTPException(status_code=404, detail="Report not found")

        status_data = _REPORT_STATUS_STORE[report_id]
        file_path = Path(status_data.get("file_path", ""))

        # Delete file if exists
        if file_path.exists():
            file_path.unlink()

        # Remove from store
        del _REPORT_STATUS_STORE[report_id]

        return {"status": "success", "message": "Report deleted"}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error deleting report: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
