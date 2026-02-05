"""Robot parsing models for parsing local keywords and their properties."""

import io
import logging
from pathlib import Path

from robot.api.parsing import (
    ModelVisitor,
)
from robot.parsing.model.blocks import (
    Keyword,
    ModelWriter,
)
from robot.parsing.model.statements import (
    Documentation,
)
from roboview.schemas.domain.keywords import KeywordProperties

logger = logging.getLogger(__name__)


class LocalKeywordFinder(ModelVisitor):
    """Visitor that collects local keywords and their properties.

    Attributes:
        keyword_doc (list[KeywordProperties]): List containing dictionaries of keywords with their properties.
        file_path (str): Path to the Robot Framework file being parsed.

    """

    def __init__(self, file_path: Path) -> None:
        """Initialize the visitor.

        Arguments:
            file_path (str): Path to the Robot Framework file being parsed.

        """
        self.keyword_doc: list[KeywordProperties] = []
        self.file_path = file_path

    def visit_Keyword(self, node: Keyword) -> None:  # noqa: N802
        """Visit a keyword node and collect its name, documentation, and prefix.

        Arguments:
            node (Keyword): The keyword definition node.

        """
        try:
            documentation = ""
            for item in node.body:
                if isinstance(item, Documentation):
                    documentation = item.value

            keyword_name_with_prefix = f"{self.file_path.stem}.{node.name}"

            self.keyword_doc.append(
                KeywordProperties(
                    file_name=self.file_path.name,
                    keyword_name_without_prefix=node.name,
                    keyword_name_with_prefix=keyword_name_with_prefix,
                    description=documentation,
                    is_user_defined=True,
                    code=self.convert_keyword_ast_to_string(node),
                    source=self.file_path.as_posix(),
                    validation_str_without_prefix=node.name.lower().replace(" ", "").replace("_", ""),
                    validation_str_with_prefix=keyword_name_with_prefix.lower().replace(" ", "").replace("_", ""),
                )
            )
        except AttributeError:
            logger.exception("Keyword node missing expected attributes")
        except Exception:
            logger.exception("Unexpected error while visiting keyword")

    @staticmethod
    def convert_keyword_ast_to_string(node: Keyword) -> str:
        """Convert a Robot Framework AST Keyword node to its string representation.

        Arguments:
            node (File): The AST node (typically a keyword or file-level node).

        Returns:
            str: The string representation of the node.

        Raises:
            Exception: If writing the model to string fails.

        """
        try:
            output = io.StringIO()
            ModelWriter(output).write(node)
            output_string = output.getvalue()
            output.close()
        except Exception:
            logger.exception("Failed to convert node to string")
            return node.name
        else:
            return output_string


class LocalKeywordNameFinder(ModelVisitor):
    """A visitor that collects all locally defined keyword names from a Robot Framework file.

    This class traverses the Robot Framework parse tree and gathers the names of all
    keywords defined in the file using the visitor pattern.

    Attributes:
        keywords (List[str]): A list that stores the names of all found keywords, capitalized using `str.title()`.

    """

    def __init__(self) -> None:
        """Initialize the LocalKeywordNameFinder."""
        self.keywords: list[str] = []

    def visit_Keyword(self, node: Keyword) -> None:  # noqa: N802
        """Visit each Keyword node and store the keyword name.

        Arguments:
            node (Keyword): The keyword node to process.

        Notes:
            The keyword name is converted to title case using `str.title()` before storing.

        Raises:
            AttributeError: If the node does not have a `name` attribute.
            Exception: For any unexpected errors during node processing.

        """
        try:
            self.keywords.append(node.name)
        except AttributeError:
            logger.exception("Keyword node missing 'name' attribute")
        except Exception:
            logger.exception("Unexpected error while visiting keyword")
