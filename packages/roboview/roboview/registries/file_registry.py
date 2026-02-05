"""File registry for centralized Robot Framework file lookup and management."""

import logging

from roboview.schemas.domain.files import FileProperties

logger = logging.getLogger(__name__)


class FileRegistry:
    """Central registry for file lookup and resolution.

    This class provides a centralized store for all Robot Framework files in a
    project, including initialized keywords and called keywords.

    Attributes:
        _file_registry: Dictionary containing all registered files.

    """

    def __init__(self) -> None:
        """Initialize an empty file registry."""
        self._file_registry: dict[str, FileProperties] = {}

    def register(self, file: FileProperties) -> None:
        """Register a file in the registry.

        Arguments:
            file: The file to register.

        """
        try:
            self._file_registry[file.file_name] = file

        except Exception:
            logger.exception("Failed to register file: %s", file.path)

    def resolve(self, file_path: str) -> FileProperties | None:
        """Resolve a file_path to its file properties object.

        Arguments:
            file_path (str): The file_path to resolve.

        Returns:
            FileProperties: File properties object if found, None otherwise.

        """
        if not file_path:
            logger.warning("Empty file path provided to resolve()")
            return None

        try:
            if result := next(
                (file for file in self.get_all_files() if file.path == file_path),
                None,
            ):
                return result

        except Exception:
            logger.exception("Error while resolving file: %s", file_path)
            return None
        else:
            return None

    def get_all_files(self) -> list[FileProperties]:
        """Get all registered Robot Framework files.

        Returns:
            List of all Robot Framework files in the registry.

        """
        return list(self._file_registry.values())

    def clear(self) -> None:
        """Clear all registered keywords."""
        self._file_registry.clear()

    def __len__(self) -> int:
        """Return the number of registered Robot Framework files."""
        return len(self._file_registry)

    def __contains__(self, file_path: str) -> bool:
        """Check if a file is registered."""
        return self.resolve(file_path) is not None
