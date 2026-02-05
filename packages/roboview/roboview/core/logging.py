"""Simple logging setup."""

import logging

import coloredlogs
from roboview.core.config import get_settings


def setup_logging() -> None:
    """Simple logging setup with colored console output.

    Features:
    - Environment-aware log levels (respects LOG_LEVEL from settings).
    - Colored console output in non-production environments.
    """
    settings = get_settings()
    environment = settings.ENVIRONMENT.lower()
    log_level_str = settings.LOG_LEVEL.upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    # Use colored logs in non-production, basic logging in production
    if environment != "production":
        coloredlogs.install(
            level=log_level, fmt="%(asctime)s - %(name)s[%(process)d] - %(levelname)s - %(message)s", reconfigure=True
        )
    else:
        logging.basicConfig(level=log_level, format="%(asctime)s - %(name)s[%(process)d] - %(levelname)s - %(message)s")
