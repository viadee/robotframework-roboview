"""Endpoint for initializing RoboView."""

import logging
from pathlib import Path

from fastapi import APIRouter, HTTPException
from roboview.schemas.dtos.common import InitializationRequest, InitializationResponse
from roboview.services.file_register_service import FileRegistryService
from roboview.services.keyword_register_service import KeywordRegistryService
from roboview.services.keyword_similarity_service import KeywordSimilarityService
from roboview.services.keyword_usage_service import KeywordUsageService
from roboview.services.robocop_register_service import RobocopRegistryService
from roboview.services.robocop_service import RobocopService
from starlette.requests import Request

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "",
    summary="Initialize RoboView",
    response_model=InitializationResponse,
    responses={
        200: {"description": "RoboView initialized."},
        400: {"description": "Invalid input data."},
        500: {"description": "Internal Server Error."},
        503: {"description": "Service is unavailable."},
    },
)
async def post_initialize_roboview(request: Request, initialization_request: InitializationRequest):  # noqa: ANN201
    """Endpoint to initialize RoboView.

    Arguments:
        request (Request): FastAPI request object.
        initialization_request (InitializationRequest): project_root_dir (str): Project root directory.

    Returns:
        InitializationResponse: Statuscode indicating whether initialization was successful.

    """
    try:
        logger.info("Initialization Requested")
        keyword_registry_service = KeywordRegistryService(Path(initialization_request.project_root_dir))
        keyword_registry_service.initialize()

        file_registry_service = FileRegistryService(Path(initialization_request.project_root_dir))
        file_registry_service.initialize()

        robocop_registry_service = RobocopRegistryService(
            Path(initialization_request.project_root_dir),
            Path(initialization_request.robocop_config_file) if initialization_request.robocop_config_file else None,
        )
        robocop_registry_service.initialize()

        request.app.state.keyword_registry = keyword_registry_service.get_keyword_registry()
        request.app.state.file_registry = file_registry_service.get_file_registry()
        request.app.state.robocop_registry = robocop_registry_service.get_robocop_registry()

        logger.info("Initialize Keyword Usage Service")
        request.app.state.keyword_usage_service = KeywordUsageService(
            request.app.state.keyword_registry, request.app.state.file_registry
        )

        logger.info("Initialize Keyword Similarity Service")
        request.app.state.keyword_similarity_service = KeywordSimilarityService(
            request.app.state.keyword_registry,
        )
        request.app.state.keyword_similarity_service.calculate_keyword_similarity_matrix()

        logger.info("Initialize Robocop Service")
        request.app.state.robocop_service = RobocopService(request.app.state.robocop_registry)
        logger.info("Initialization Successfull")

    except Exception as e:
        logger.exception("Error initializing Keyword List")
        raise HTTPException(status_code=500, detail="Internal Server Error") from e
    else:
        return InitializationResponse(status="success")
