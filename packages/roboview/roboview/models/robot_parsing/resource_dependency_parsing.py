"""Robot parsing models for finding import relationships between resource files."""

import logging
from pathlib import PurePosixPath

from robot.api.parsing import (
    ModelVisitor,
)
from robot.parsing import Token
from robot.parsing.model.blocks import (
    SettingSection,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResourceDependencyFinder(ModelVisitor):
    """Visitor that finds all resource import statements in the SettingSection of a Robot Framework resource file."""

    def __init__(self) -> None:
        """Initialize the ImportStatementFinder.

        Attributes:
            imports (List[str]): List of imported resource file names (without paths).

        """
        self.imports: list[str] = []

    def visit_SettingSection(self, node: SettingSection) -> None:  # noqa: N802
        """Visit the SettingSection and collect all resource import statements.

        Arguments:
            node (SettingSection): The setting section node to inspect.

        """
        for item in node.body:
            try:
                if item.type == "RESOURCE":  # pyright: ignore[reportAttributeAccessIssue]
                    import_value = item.get_value(Token.NAME)  # pyright: ignore[reportAttributeAccessIssue]

                    if import_value is None:
                        logger.exception("Import value is None.")
                        continue

                    if not isinstance(import_value, str):
                        logger.exception("Expected a string but got unknown.")
                        continue

                    normalized_import_value = import_value.replace("{/}", "/").replace("${/}", "/")

                    referenced_filename = PurePosixPath(normalized_import_value).name
                    self.imports.append(referenced_filename)
            except AttributeError:
                logger.exception("Setting item missing, expected attributes")
            except Exception:
                logger.exception("Unexpected error while processing import statement")
