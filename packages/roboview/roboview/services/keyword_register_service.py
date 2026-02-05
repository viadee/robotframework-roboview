"""Service for keyword registry management."""

import logging
from pathlib import Path

from robot.libdocpkg import LibraryDocumentation
from robot.parsing import get_model, get_resource_model
from roboview.models.robot_parsing.keyword_dependency_parsing import KeywordDependencyFinder
from roboview.models.robot_parsing.local_keyword_parsing import LocalKeywordFinder
from roboview.registries.keyword_registry import KeywordRegistry
from roboview.schemas.domain.common import FileType, LibraryType
from roboview.schemas.domain.keywords import KeywordProperties
from roboview.utils.directory_parsing import DirectoryParser

logger = logging.getLogger(__name__)


class KeywordRegistryService:
    """Service that orchestrates keyword parsing and registry population.

    This service coordinates the parsing of Robot Framework files and the population
    of the KeywordRegistry. It separates the concerns of:
    - File discovery (via DirectoryParser)
    - Data extraction (via Robot Framework Parsers)
    - Data storage and lookup (via KeywordRegistry)

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
        self.registry = KeywordRegistry()

    def initialize(self) -> None:
        """Initialize the keyword registry by loading all keywords.

        This method:
        1. Loads local keywords from .robot and .resource files
        2. Loads external library keywords (Browser, Selenium, Database, BuiltIn)
        3. Populates the KeywordRegistry with all discovered keywords

        """
        try:
            self._load_local_keywords()
            self._load_library_keywords()
            logger.info("Registry initialized with %d keywords", len(self.registry))
        except Exception:
            logger.exception("Failed to initialize keyword registry")

    def _load_local_keywords(self) -> None:
        """Load local keywords from Robot Framework files."""
        try:
            robot_files = self.directory_parser.get_test_file_paths()
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

        for robot_file in robot_files:
            try:
                self._parse_and_register_file(robot_file, FileType.ROBOT)
            except Exception:
                logger.exception("Failed to process robot file: %s", robot_file.name)
                continue

    def _parse_and_register_file(self, file_path: Path, file_type: FileType) -> None:
        """Parse a single file and register its keywords.

        Arguments:
            file_path: Path to the Robot Framework file.
            file_type: file_type: Whether it is a ROBOT or RESOURCE file.

        """
        try:
            model = get_resource_model(file_path) if file_type.RESOURCE else get_model(file_path)

            local_kw_parser = LocalKeywordFinder(file_path)
            local_kw_parser.visit(model)

            kw_dependency_finder = KeywordDependencyFinder(file_path)
            kw_dependency_finder.visit(model)

            for keyword in local_kw_parser.keyword_doc:
                enriched_keyword = self._enrich_with_called_keywords(kw_dependency_finder, keyword)
                self.registry.register(enriched_keyword)

        except Exception:
            logger.exception("Error parsing file: %s", file_path)

    @staticmethod
    def _enrich_with_called_keywords(
        keyword_dependency_finder: KeywordDependencyFinder, keyword_doc: KeywordProperties
    ) -> KeywordProperties:
        """Add found called keywords to an KeywordProperties object.

        Arguments:
            keyword_dependency_finder (KeywordDependencyFinder): Initialized KeywordDependencyFinder instance.
            keyword_doc: KeywordProperties object for the particular keyword.

        Returns:
            KeywordProperties: KeywordProperties object with called keywords.

        """
        dependency_map = {
            item["keyword_name"]: item["called_keywords"] for item in keyword_dependency_finder.get_formatted_result()
        }

        keyword_name = keyword_doc.keyword_name_without_prefix
        keyword_doc.called_keywords = dependency_map.get(keyword_name, [])
        return keyword_doc

    def _load_library_keywords(self) -> None:
        """Load keywords from external Robot Framework libraries."""
        libraries = [
            LibraryType.BROWSER,
            LibraryType.SELENIUM,
            LibraryType.DATABASE,
            LibraryType.BUILTIN,
        ]

        for library_type in libraries:
            try:
                keyword_doc = self._get_library_keywords(library_type)
                for keyword in keyword_doc:
                    self.registry.register(keyword)

            except Exception:
                logger.exception("Failed to load library: %s", library_type.value)
                continue

    @staticmethod
    def _get_library_keywords(library_type: LibraryType) -> list[KeywordProperties]:
        """Get keyword metadata for a specific library.

        Arguments:
            library_type: The library type to load.

        Returns:
            List of KeywordProperties for the library.

        """
        lib_name = library_type.value
        keywords_metadata = []

        try:
            lib = LibraryDocumentation(lib_name)
            for keyword in lib.keywords:
                keyword_with_prefix = f"{lib_name}.{keyword.name}"

                keywords_metadata.append(
                    KeywordProperties(
                        file_name=lib_name,
                        keyword_name_without_prefix=keyword.name,
                        keyword_name_with_prefix=str(keyword_with_prefix),
                        description=keyword.doc,
                        is_user_defined=False,
                        code="",
                        source=lib_name,
                        validation_str_without_prefix=keyword.name.lower().replace(" ", "").replace("_", ""),
                        validation_str_with_prefix=str(keyword_with_prefix).lower().replace(" ", "").replace("_", ""),
                    )
                )

        except Exception:
            logger.exception("Library %s could not be loaded", lib_name)
            return []

        return keywords_metadata

    def get_keyword_info_list(self) -> list[KeywordProperties]:
        """Get all keywords as list of dictionaries (for backward compatibility).

        Returns:
            List of dictionaries with keyword information.

        """
        return self.registry.get_all_keywords()

    def get_keyword_registry(self) -> KeywordRegistry:
        """Function to return the keyword registry object.

        Returns:
            KeywordRegistry: Initialized KeywordRegistry object.

        """
        return self.registry
