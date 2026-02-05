"""Robocop registry for centralized error messages lookup and management."""

import logging

from roboview.schemas.domain.robocop import RobocopMessage

logger = logging.getLogger(__name__)


class RobocopRegistry:
    """Central registry for Robocop error messages.

    This class provides a centralized store for all Robocop error messages in a project.

    Attributes:
        _robocop_registry: Dictionary containing all registered Robocop messages.

    """

    def __init__(self) -> None:
        """Initialize an empty Robocop registry."""
        self._robocop_registry: dict[str, RobocopMessage] = {}

    def register(self, error_message: RobocopMessage) -> None:
        """Register an error message in the registry.

        Arguments:
            error_message: Error message to register.

        """
        try:
            self._robocop_registry[error_message.message_id] = error_message

        except Exception:
            logger.exception("Failed to register error message: %s", error_message.message)

    def resolve(self, message_id: str) -> RobocopMessage | None:
        """Resolve an error message to its RobocopMessage object.

        Arguments:
            message_id (str): The message_id as uuid4 string.

        Returns:
            list[RobocopMessages]: List of found RobocopMessage objects.

        """
        if not message_id:
            logger.warning("Empty message_id provided to resolve()")
            return None

        try:
            if result := next(
                (message for message in self.get_all_error_messages() if message.message_id == message_id),
                None,
            ):
                return result

        except Exception:
            logger.exception("Error while resolving messages for message with id: %s", message_id)
            return None
        else:
            return None

    def get_all_error_messages(self) -> list[RobocopMessage]:
        """Get all registered error messages.

        Returns:
            List of all error messages with metadata in the registry.

        """
        return list(self._robocop_registry.values())

    def clear(self) -> None:
        """Clear all registered Robocop messages."""
        self._robocop_registry.clear()

    def __len__(self) -> int:
        """Return the number of registered error messages."""
        return len(self._robocop_registry)

    def __contains__(self, file_path: str) -> bool:
        """Check if a file contains error messages that are registered."""
        return self.resolve(file_path) is not None
