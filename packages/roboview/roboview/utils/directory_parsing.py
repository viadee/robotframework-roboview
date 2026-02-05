"""Parse test- and resource file paths from a root directory."""

import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DirectoryParser:
    """Class to go through a directory and store all robot- and resource file paths."""

    def __init__(self, project_root_path: Path) -> None:
        """Initialize the DirectoryParser with a project directory path."""
        self.project_root_path = project_root_path

    def get_test_file_paths(self) -> list[Path]:
        """Retrieve a list of all '.robot' test file paths under the project root directory.

        This method recursively searches through all subdirectories starting from
        `self.project_root_path` and collects files that match the '*.robot' pattern.

        Returns:
            List[Path]: A list of Path objects pointing to '.robot' files.

        Raises:
            OSError: If there's an issue accessing the file system (e.g., permission denied).

        """
        try:
            return list(self.project_root_path.rglob("*.robot"))
        except OSError:
            logger.exception("Error while searching for .robot files")
            raise

    def get_resource_file_paths(self) -> list[Path]:
        """Retrieve a list of all '.resource' file paths under the project root directory.

        This method recursively searches through all subdirectories starting from
        `self.project_root_path` and collects files that match the '*.resource' pattern.

        Returns:
            List[Path]: A list of Path objects pointing to '.resource' files.

        Raises:
            OSError: If there's an issue accessing the file system (e.g., permission denied).

        """
        try:
            return list(self.project_root_path.rglob("*.resource"))
        except OSError:
            logger.exception("Error while searching for .resource files")
            raise
