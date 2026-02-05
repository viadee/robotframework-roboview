"""Global settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


# ANSI config codes for terminal output
class CONFIG:
    """Configuration class for ANSI config codes."""

    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def print_warning(message: str) -> None:
    """Print a colored warning message."""
    print(f"{CONFIG.YELLOW}{CONFIG.BOLD}WARNING:{CONFIG.RESET} {CONFIG.YELLOW}{message}{CONFIG.RESET}")  # noqa: T201


class Settings(BaseSettings):
    """Settings class with environment variables."""

    # Base Project Settings
    PROJECT_NAME: str = Field(default="RoboView")
    API_VERSION_STR: str = Field(default="/api/v1")
    APP_VERSION: str = Field(default="0.1.0")

    # Environment - default to development
    ENVIRONMENT: str = Field(default="production")

    # Logging settings - default to INFO
    LOG_LEVEL: str = Field(default="INFO")

    # Middleware settings
    BACKEND_CORS_ORIGINS: list[str] = Field(default=["http://localhost:8000"])
    HTTP_METHODS: list[str] = Field(default=["GET", "POST", "PUT", "DELETE"])


@lru_cache
def get_settings() -> Settings:
    """Initialize settings."""
    return Settings()
