"""Robot parsing model to find keyword dependencies between keywords."""

import logging
from pathlib import Path

from robot.api.parsing import (
    ModelVisitor,
)
from robot.parsing.model.blocks import (
    Keyword,
)
from robot.parsing.model.statements import (
    KeywordCall,
)

logger = logging.getLogger(__name__)


class KeywordDependencyFinder(ModelVisitor):
    """Visitor that finds keyword dependencies for keywords within a .resource or .robot file.

    This class analyzes Robot Framework files to identify which keywords are called
    by other keywords, creating a dependency mapping that can be used for analysis
    and visualization of keyword relationships.

    Attributes:
        current_keyword (Optional[str]): The keyword currently being visited.
        keyword_calls (Dict[str, List[str]]): Mapping from keyword to its called keywords.

    """

    def __init__(self, file_path: Path) -> None:
        """Initialize visitor for identifying keyword dependencies based on keyword calls.

        Arguments:
            file_path (Path): The path of the analyzed Robot Framework file.


        Attributes:
            file_path (Path): The path of the analyzed Robot Framework file.

        """
        self.current_keyword: str
        self.keyword_calls = {}
        self.file_path = file_path

    def visit_Keyword(self, node: Keyword) -> None:  # noqa: N802
        """Visit a keyword node and set up context for analyzing its dependencies.

        Arguments:
            node (Keyword): The keyword definition node from the Robot Framework AST.

        """
        try:
            self.current_keyword = node.name
            self.keyword_calls[self.current_keyword] = []
            self.generic_visit(node)
        except AttributeError:
            logger.exception("Keyword node missing expected name attribute")
        except Exception:
            logger.exception("Unexpected error while visiting keyword: %s", getattr(node, "name", "Unknown"))

    def visit_KeywordCall(self, node: KeywordCall) -> None:  # noqa: N802
        """Analyze keyword calls within the current keyword to build dependency mapping.

        Arguments:
            node (KeywordCall): The keyword call statement node.

        """
        if self.current_keyword is None:
            return

        try:
            called_name = node.keyword or None

            if not called_name:
                return

            self.keyword_calls[self.current_keyword].append(called_name)

        except AttributeError:
            logger.exception("KeywordCall node missing expected keyword attribute")
        except Exception:
            logger.exception("Unexpected error while processing keyword call in keyword: %s", self.current_keyword)

    def get_formatted_result(self) -> list[dict]:
        """Return dependency mapping in structured format.

        Returns:
            list[dict]: List of dictionaries containing keyword dependency information.
                Each dictionary has keys: 'file_name', 'keyword_name', 'called_keywords'.

        """
        try:
            return [
                {
                    "file_path": self.file_path.as_posix(),
                    "file_name": self.file_path.name,
                    "keyword_name": keyword,
                    "called_keywords": list(set(called_keywords)),
                }
                for keyword, called_keywords in self.keyword_calls.items()
            ]
        except Exception:
            logger.exception("Error while formatting keyword dependency results")
            return []
