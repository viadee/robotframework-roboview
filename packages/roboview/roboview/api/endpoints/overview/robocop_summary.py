"""Endpoint for fetching a robocop issue summary."""

import logging

from fastapi import APIRouter, HTTPException
from roboview.schemas.dtos.overview import RobocopIssueSummaryResponse
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    summary="Get Robocop issue summary",
    response_model=RobocopIssueSummaryResponse,
    responses={
        200: {"description": "Robocop issue summary fetched successfully."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def get_robocop_issue_summary(request: Request):  # noqa: ANN201
    """Endpoint to fetch a robocop issue summary for the RoboView overview page.

    Arguments:
        request (Request): FastAPI request object.

    Returns:
        RobocopIssueSummaryResponse: List containing an issue summary w.r.t the issue category.

    """
    try:
        issue_summary = request.app.state.robocop_service.get_robocop_issue_summary()

    except Exception as e:
        logger.exception("Error calculating KPIs")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    else:
        return RobocopIssueSummaryResponse(robocop_issue_summary=issue_summary)
