"""Endpoints for report generation and management."""

import logging
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import anyio
from fastapi import APIRouter, HTTPException
from roboview.schemas.dtos.reports import GenerateReportRequest, ReportStatusResponse
from roboview.utils.exporters.html_exporter import HTMLExporter
from starlette.requests import Request
from starlette.responses import FileResponse

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory store for report status (in production, would use database)
_REPORT_STATUS_STORE: dict[str, dict] = {}


def _get_report_or_raise(report_id: str) -> dict:
    """Get report from store or raise HTTPException."""
    if report_id not in _REPORT_STATUS_STORE:
        raise HTTPException(status_code=404, detail="Report not found")
    return _REPORT_STATUS_STORE[report_id]


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
        created_at = datetime.now(UTC).isoformat()

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
    except Exception:
        logger.exception("Error generating report")
        report_id_local = str(uuid4())
        _REPORT_STATUS_STORE[report_id_local] = {
            "status": "failed",
            "error": "Internal error",
        }
        raise HTTPException(status_code=500, detail="Internal Server Error") from None


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
        status_data = _get_report_or_raise(report_id)
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
    except Exception:
        logger.exception("Error retrieving report status")
        raise HTTPException(status_code=500, detail="Internal Server Error") from None


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
    status_data = _get_report_or_raise(report_id)

    if status_data["status"] != "completed":
        raise HTTPException(status_code=400, detail="Report generation not completed")

    file_path = anyio.Path(status_data["file_path"])

    try:
        if not await file_path.exists():
            raise HTTPException(status_code=404, detail="Report file not found")  # noqa: TRY301

        return FileResponse(
            Path(status_data["file_path"]),
            media_type="text/html",
            filename=f"report_{report_id[:8]}.html",
        )

    except HTTPException:
        raise
    except Exception:
        logger.exception("Error downloading report")
        raise HTTPException(status_code=500, detail="Internal Server Error") from None


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
        reports = [
            {
                "report_id": report_id,
                "report_type": status_data["report_type"],
                "export_format": status_data["export_format"],
                "created_at": status_data["created_at"],
                "file_size": status_data.get("file_size"),
                "status": status_data["status"],
            }
            for report_id, status_data in _REPORT_STATUS_STORE.items()
            if status_data["status"] == "completed"
        ]
    except Exception:
        logger.exception("Error retrieving available reports")
        raise HTTPException(status_code=500, detail="Internal Server Error") from None
    else:
        return reports


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
    status_data = _get_report_or_raise(report_id)
    file_path = anyio.Path(status_data.get("file_path", ""))

    try:
        # Delete file if exists
        if await file_path.exists():
            await file_path.unlink()

        # Remove from store
        del _REPORT_STATUS_STORE[report_id]
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error deleting report")
        raise HTTPException(status_code=500, detail="Internal Server Error") from None
    else:
        return {"status": "success", "message": "Report deleted"}
