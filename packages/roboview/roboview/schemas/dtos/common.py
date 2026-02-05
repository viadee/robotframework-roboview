"""Common schemas for pydantic validation."""

from pathlib import Path

from pydantic import BaseModel, Field


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = Field(default="OK", description="Status of the health check")


class Shutdown(BaseModel):
    """Response model to validate and return when performing a shutdown."""

    status: str = Field(default="Server is shutting down...", description="Whether the shutdown was successful")


class InitializationRequest(BaseModel):
    """Request model to validate and return when requesting an initialization."""

    project_root_dir: Path = Field(description="Path to the project root directory")
    robocop_config_file: Path | None = Field(description="Path to the Robocop config file", default=None)


class InitializationResponse(BaseModel):
    """Response model to validate and return when performing an initialization."""

    status: str = Field(default="OK", description="Whether the initialization was successful")
