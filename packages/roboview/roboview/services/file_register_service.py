"""Service for file registry management."""

import logging
from pathlib import Path

from robot.parsing import get_model, get_resource_model
from roboview.models.robot_parsing.called_keyword_parsing import CalledKeywordFinder
from roboview.models.robot_parsing.local_keyword_parsing import LocalKeywordNameFinder
from roboview.models.robot_parsing.resource_dependency_parsing import ResourceDependencyFinder
from roboview.registries.file_registry import FileRegistry
from roboview.schemas.domain.common import FileType
from roboview.schemas.domain.files import FileProperties
from roboview.utils.directory_parsing import DirectoryParser

logger = logging.getLogger(__name__)


class FileRegistryService:
    """Service that orchestrates file registry population.

    This service coordinates the parsing of Robot Framework files and the population
    of the FileRegistry. It separates the concerns of:
    - File discovery (via DirectoryParser)
    - Data extraction (via Robot Framework Parsers)
    - Data storage and lookup (via KeywordRegistry and FileRegistry)

    Attributes:
        directory_parser: Parser for discovering Robot Framework files.
        registry: Central registry for keyword lookup.

    """

    def __init__(self, project_root_dir: Path) -> None:
        """Initialize the keyword analysis service.

        Arguments:
            project_root_dir (Path): Path to the project root directory.

        """
        self.directory_parser = DirectoryParser(project_root_dir)
        self.file_registry = FileRegistry()

    def initialize(self) -> None:
        """Initialize the file registry by loading all files.

        This method:
        1. Loads all Robot Frameworks files with their corresponding initialized and called keywords
        2. Populates the FileRegistry with all discovered files

        """
        try:
            self._load_resource_files()
            self._load_robot_files()
            logger.info("Registry initialized with %d files", len(self.file_registry))
        except Exception:
            logger.exception("Failed to initialize file registry")

    def _load_robot_files(self) -> None:
        """Load robot files."""
        try:
            robot_files = self.directory_parser.get_test_file_paths()
        except Exception:
            logger.exception("Failed to retrieve file paths from directory parser")
            return

        for robot_file in robot_files:
            try:
                self._parse_and_register_file(robot_file, FileType.ROBOT)
            except Exception:
                logger.exception("Failed to process robot file: %s", robot_file.name)
                continue

    def _load_resource_files(self) -> None:
        """Load resource files."""
        try:
            resource_files = self.directory_parser.get_resource_file_paths()
        except Exception:
            logger.exception("Failed to retrieve file paths from directory parser")
            return

        for resource_file in resource_files:
            try:
                self._parse_and_register_file(resource_file, FileType.RESOURCE)
            except Exception:
                logger.exception("Failed to process resource file: %s", resource_file.name)
                continue

    def _parse_and_register_file(self, file_path: Path, file_type: FileType) -> None:
        """Parse a single file and register its initialized and called keywords.

        Arguments:
            file_path: Path to the Robot Framework file.
            file_type: Whether it is a ROBOT or RESOURCE file.

        """
        try:
            model = get_resource_model(file_path) if file_type is file_type.RESOURCE else get_model(file_path)

            initialized_kw_parser = LocalKeywordNameFinder()
            initialized_kw_parser.visit(model)

            called_kw_parser = CalledKeywordFinder()
            called_kw_parser.visit(model)

            resource_dependency_parser = ResourceDependencyFinder()
            resource_dependency_parser.visit(model)

            self.file_registry.register(
                FileProperties(
                    file_name=file_path.name,
                    path=file_path.as_posix(),
                    is_resource=bool(file_type is FileType.RESOURCE),
                    initialized_keywords=initialized_kw_parser.keywords,
                    called_keywords=called_kw_parser.called_keywords,
                    imported_files=resource_dependency_parser.imports,
                )
            )

        except Exception:
            logger.exception("Error parsing file: %s", file_path)

    def get_file_info_list(self) -> list[FileProperties]:
        """Get all files as list of dictionaries.

        Returns:
            List of dictionaries with file information.

        """
        return self.file_registry.get_all_files()

    def get_file_registry(self) -> FileRegistry:
        """Function to return the file registry object.

        Returns:
            FileRegistry: Initialized FileRegistry object.

        """
        return self.file_registry
