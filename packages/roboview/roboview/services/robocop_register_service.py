"""Service for RobocopRegistry management."""

import logging
import os
import re
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import click
from robocop.config import Config, ConfigManager
from robocop.linter.runner import RobocopLinter
from roboview.registries.robocop_registry import RobocopRegistry
from roboview.schemas.domain.robocop import RobocopMessage, RuleCategory
from roboview.utils.directory_parsing import DirectoryParser

logger = logging.getLogger(__name__)


class RobocopRegistryService:
    """Service that orchestrates RobocopRegistry population.

    This service coordinates the parsing of Robocop error messages and the population
    of the RobocopRegistry.

    Attributes:
        project_root_dir (Path): Path to the root directory of the project.
        directory_parser: Parser for discovering Robot Framework files.
        robocop_config_file: User defined config file for the Robocop linter.
        robocop_registry: Central registry for error message lookup.

    """

    def __init__(self, project_root_dir: Path, robocop_config_file: Path | None) -> None:
        """Initialize the RobocopRegistryService.

        Arguments:
            project_root_dir (Path): Path to the project root directory.
            robocop_config_file (Path | None): Path to the Robocop configuration file.

        """
        self.project_root_dir = project_root_dir
        self.directory_parser = DirectoryParser(project_root_dir)
        self.robocop_config_file = robocop_config_file
        self.robocop_registry = RobocopRegistry()

    def initialize(self) -> None:
        """Initialize the RobocopRegistry by loading all files.

        This method:
        1. Loads all Robot Frameworks files and checks whether errors are present.
        2. Populates the RobocopRegistry with all discovered error messages.

        """
        try:
            self._extract_diagnostics()
            logger.info("Registry initialized with %d error messages", len(self.robocop_registry))
        except Exception:
            logger.exception("Failed to initialize file registry")

    def _extract_diagnostics(self) -> None:
        """Extract diagnostics from Robocop run and populates the robocop registry."""
        config_manager = self._get_robocop_config_manager()

        if config_manager is None:
            self._parse_and_register_files()
            return

        linter = RobocopLinter(config_manager)
        try:
            with open(os.devnull, "w") as devnull, redirect_stdout(devnull), redirect_stderr(devnull):  # noqa: PTH123
                linter.run()
        except click.exceptions.Exit:
            diagnostics = linter.diagnostics
            if diagnostics:
                for error in diagnostics:
                    rf_script_path = Path(error.source)
                    self.robocop_registry.register(
                        RobocopMessage(
                            rule_id=self._extract_rule_id(str(error.rule)),
                            rule_message=str(error.rule),
                            message=str(error.message),
                            category=self._extract_rule_category(str(error.rule)),
                            file_name=rf_script_path.name,
                            source=rf_script_path.as_posix(),
                            severity=str(error.severity),
                            code=self.format_code_snippet(
                                self.extract_code_snippet(
                                    rf_script_path,
                                    error.range.start.line,
                                    error.range.start.character,
                                    error.range.end.line,
                                    error.range.end.character,
                                )
                            ),
                        )
                    )
        except Exception:
            logger.exception("Failed to extract diagnostics from Robocop run")

    def _parse_and_register_files(self) -> None:
        """Check a single file with the Robocop linter."""
        dir_parser = self.directory_parser
        robot_files = dir_parser.get_test_file_paths()
        resources_files = dir_parser.get_resource_file_paths()
        files = robot_files + resources_files

        try:
            config = Config(silent=True)
            linter = RobocopLinter(ConfigManager())

            for file in files:
                diagnostics = linter.get_model_diagnostics(config, file)

                if diagnostics:
                    for error in diagnostics:
                        self.robocop_registry.register(
                            RobocopMessage(
                                rule_id=self._extract_rule_id(str(error.rule)),
                                rule_message=str(error.rule),
                                message=str(error.message),
                                category=self._extract_rule_category(str(error.rule)),
                                file_name=file.name,
                                source=file.as_posix(),
                                severity=str(error.severity),
                                code=self.format_code_snippet(
                                    self.extract_code_snippet(
                                        file,
                                        error.range.start.line,
                                        error.range.start.character,
                                        error.range.end.line,
                                        error.range.end.character,
                                    )
                                ),
                            )
                        )

        except Exception:
            logger.exception("Error parsing files")

    @staticmethod
    def _extract_rule_id(rule_text: str) -> str:
        """Extract rule ID from robocop rule text.

        Arguments:
            rule_text (str): Robocop rule text.

        Returns:
            str: Rule ID e.g VAR01. or "" if not found.

        """
        if match := re.search(r"\[([A-Z0-9]+)\]", rule_text):
            return match.group(1)
        return ""

    @staticmethod
    def _extract_rule_category(rule_text: str) -> RuleCategory | str:
        """Extract the exact rule category from Robocop rule text.

        Arguments:
            rule_text (str): Robocop rule text.

        Returns:
            str: Rule category e.g ARG for arguments.

        """
        category_mapping = {
            "ARG": RuleCategory.ARG,
            "COM": RuleCategory.COM,
            "DEPR": RuleCategory.DEPR,
            "DOC": RuleCategory.DOC,
            "DUP": RuleCategory.DUP,
            "ERR": RuleCategory.ERR,
            "IMP": RuleCategory.IMP,
            "KW": RuleCategory.KW,
            "LEN": RuleCategory.LEN,
            "MISC": RuleCategory.MISC,
            "NAME": RuleCategory.NAME,
            "ORD": RuleCategory.ORD,
            "SPC": RuleCategory.SPC,
            "TAG": RuleCategory.TAG,
            "VAR": RuleCategory.VAR,
            "ANN": RuleCategory.ANN,
        }

        if match := re.search(r"\[([A-Z]+)\d+\]", rule_text):
            prefix = match.group(1)
            return category_mapping.get(prefix, "")

        return ""

    def _get_robocop_config_manager(self) -> ConfigManager | None:
        """Return a ConfigManager object using either a user-defined config file or a default one."""
        dir_parser = self.directory_parser
        robot_files = dir_parser.get_test_file_paths()
        robot_files_str = [str(p) for p in robot_files]
        resources_files = dir_parser.get_resource_file_paths()
        resources_files_str = [str(p) for p in resources_files]
        files = robot_files_str + resources_files_str

        if self.robocop_config_file is None:
            try:
                return ConfigManager(sources=files)
            except Exception:
                logger.exception("Robocop config is probably invalid. Using default config instead.")
                return None
        if self.robocop_config_file.exists() & self._check_robocop_config():
            return ConfigManager(sources=files, config=self.robocop_config_file)
        return None

    def _check_robocop_config(self) -> bool:
        """Checks whether the given Robocop config file is a valid config file.

        Returns:
            bool: True if the config file is valid, False otherwise.

        """
        try:
            ConfigManager(config=self.robocop_config_file)
        except click.exceptions.Exit:
            logger.warning(
                "Given Robocop config file is deprecated and needs to be migrated to robocop > 6.0.0 "
                "Using default config instead."
            )
            return False
        else:
            return True

    @staticmethod
    def extract_code_snippet(  # noqa: PLR0913
        file_path: Path,
        line: int,
        column: int,
        end_line: int | None = None,
        end_column: int | None = None,
        context_lines: int = 1,
    ) -> dict:
        """Extract code snippet with context from a file.

        Arguments:
            file_path: Path to the source file
            line: Starting line number (1-indexed)
            column: Starting column number (1-indexed)
            end_line: Ending line number (optional)
            end_column: Ending column number (optional)
            context_lines: Number of context lines to show before and after

        Returns:
            Dictionary with code snippet and highlighting information

        """
        try:
            with file_path.open(encoding="utf-8") as f:
                lines = f.readlines()
        except (FileNotFoundError, UnicodeDecodeError):
            return {}

        # Convert to 0-indexed
        line_idx = line - 1
        end_line_idx = (end_line - 1) if end_line else line_idx

        # Calculate context range
        start_context = max(0, line_idx - context_lines)
        end_context = min(len(lines), end_line_idx + context_lines + 1)

        # Extract lines with context
        snippet_lines = []
        for i in range(start_context, end_context):
            line_number = i + 1
            line_content = lines[i].rstrip("\n")

            # Mark the error line(s)
            is_error_line = line_idx <= i <= end_line_idx

            snippet_lines.append(
                {
                    "line_number": line_number,
                    "content": line_content,
                    "is_error": is_error_line,
                }
            )

        # Calculate highlight position for the error line
        error_line_content = lines[line_idx] if line_idx < len(lines) else ""
        highlight_start = column - 1  # Convert to 0-indexed
        highlight_end = end_column - 1 if end_column else len(error_line_content.rstrip())

        return {
            "lines": snippet_lines,
            "error_line": line,
            "error_column": column,
            "highlight_start": highlight_start,
            "highlight_end": highlight_end,
            "highlighted_text": error_line_content[highlight_start:highlight_end].strip(),
        }

    @staticmethod
    def format_code_snippet(snippet: dict) -> str:
        """Format code snippet in a readable way similar to Robocop output.

        Arguments:
            snippet (dict): Code snipped, where the error occured.

        Returns:
            str: Formatted code snippet with highlighting.

        """
        if not snippet or "lines" not in snippet:
            return ""

        lines = snippet["lines"]
        error_line = snippet["error_line"]
        highlight_start = snippet["highlight_start"]
        highlight_end = snippet["highlight_end"]

        # Calculate max line number width for alignment
        max_line_num = max(line["line_number"] for line in lines)
        line_width = len(str(max_line_num))

        output = []
        output.append(" " * (line_width + 1) + "|")

        for line in lines:
            line_num = str(line["line_number"]).rjust(line_width)
            output.append(f"{line_num} | {line['content']}")

            # Add highlight marker under error line
            if line["line_number"] == error_line:
                marker_indent = " " * (line_width + 1) + "|"
                highlight_length = highlight_end - highlight_start
                marker = " " * highlight_start + "^" * max(1, highlight_length)
                # Add label if available
                output.append(f"{marker_indent} {marker}")

        return "\n".join(output)

    def get_error_message_list(self) -> list[RobocopMessage]:
        """Get all error messages as list of dictionaries.

        Returns:
            list[RobocopMessage]: List of all registered RobocopMessage objects.

        """
        return self.robocop_registry.get_all_error_messages()

    def get_robocop_registry(self) -> RobocopRegistry:
        """Function to return the file registry object.

        Returns:
            FileRegistry: Initialized FileRegistry object.

        """
        return self.robocop_registry
