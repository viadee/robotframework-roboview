"""Class to provide the Robot Framework RoboCop functionality."""

import logging
from collections import Counter

from roboview.registries.robocop_registry import RobocopRegistry
from roboview.schemas.domain.robocop import IssueSummary, RobocopMessage

logger = logging.getLogger(__name__)


class RobocopService:
    """Class to provide the Robot Framework RoboCop functionality.

    Arguments:
        robocop_registry (RobocopRegistry): Initialized RobocopRegistry object.

    Attributes:
        robocop_registry (RobocopRegistry): Initialized RobocopRegistry object.

    """

    def __init__(self, robocop_registry: RobocopRegistry) -> None:
        """Initialize RobocopService."""
        self.robocop_registry = robocop_registry

    def get_robocop_error_messages(self) -> list[RobocopMessage]:
        """Return all registered robocop error messages.

        Returns:
            list[RobocopMessage]: List of all Robocop error messages.

        """
        try:
            return self.robocop_registry.get_all_error_messages()
        except Exception:
            logger.exception("Failed to get robocop error messages")
            return []

    def get_robocop_message_by_id(self, message_id: str) -> RobocopMessage | None:
        """Return specific robocop message by its message identifier.

        Arguments:
            message_id (str): Message identifier.

        Returns:
            RobocopMessage | None: Robocop message if found, else None.

        """
        try:
            if not message_id:
                logger.warning("Empty message_id provided to get_robocop_message_by_id")
                return None
            return self.robocop_registry.resolve(message_id)
        except Exception:
            logger.exception("Failed to get robocop message by id '%s'", message_id)
            return None

    def get_robocop_issue_summary(self) -> list[IssueSummary]:
        """Return a Robocop issue summary for all registered Robocop issues.

        Returns:
            list[IssueSummary]: List of issue summaries sorted by count in descending order.

        """
        try:
            error_messages = self.robocop_registry.get_all_error_messages()

            if not error_messages:
                logger.info("No robocop error messages found for issue summary")
                return []

            counter = Counter(msg.category for msg in error_messages if hasattr(msg, "category"))

            result = []
            for category, count in counter.items():
                try:
                    result.append(
                        IssueSummary(
                            category=category,
                            count=count,
                        )
                    )
                except Exception:
                    logger.exception("Failed to create IssueSummary for category '%s'", category)
                    continue

            return sorted(result, key=lambda x: x.count, reverse=True)
        except Exception:
            logger.exception("Failed to get robocop issue summary")
            return []
