"""Robot parsing model for parsing called keywords in a Robot Framework file."""

import logging

from robot.api.parsing import (
    ModelVisitor,
)
from robot.parsing.model.statements import (
    KeywordCall,
    Setup,
    Teardown,
    TestSetup,
    TestTeardown,
)

logger = logging.getLogger(__name__)


class CalledKeywordFinder(ModelVisitor):
    """Visitor that collects all keyword calls from a Robot Framework file.

    Attributes:
        called_keywords (List[str]): A list of keyword names that are called.

    """

    def __init__(self) -> None:
        """Initialize the CalledKeywords visitor."""
        self.called_keywords: list[str] = []
        self.bdd_prefixes: list[str] = ["given", "when", "then", "and", "but"]

    def _add_keyword(self, keyword_name: str) -> None:
        """Helper method to resolve and append a keyword name.

        Arguments:
            keyword_name (str): The used keyword name from the node.

        """
        try:
            keyword_name_without_bbd_prefix = self._ignore_bdd_prefixes(keyword_name)
            self.called_keywords.append(keyword_name_without_bbd_prefix)
        except Exception:
            logger.exception("Error while adding node to keyword list")

    def visit_KeywordCall(self, node: KeywordCall) -> None:  # noqa: N802
        """Visit a keyword call and extract the keyword.

        Arguments:
            node (KeywordCall): KeywordCall node in the AST.

        """
        self._add_keyword(node.keyword)

    def visit_Setup(self, node: Setup) -> None:  # noqa: N802
        """Visit a Setup node and extract the keyword.

        Arguments:
            node (Setup): Setup node in the AST.

        """
        self._add_keyword(node.name)

    def visit_Teardown(self, node: Teardown) -> None:  # noqa: N802
        """Visit a Teardown node and extract the keyword.

        Arguments:
            node (Teardown): Teardown node in the AST.

        """
        self._add_keyword(node.name)

    def visit_TestSetup(self, node: TestSetup) -> None:  # noqa: N802
        """Visit a TestSetup node and extract the keyword.

        Arguments:
            node (TestSetup): TestSetup node in the AST.

        """
        self._add_keyword(node.name)

    def visit_TestTeardown(self, node: TestTeardown) -> None:  # noqa: N802
        """Visit a TestTeardown node and extract the keyword.

        Arguments:
            node (TestTeardown): TestTeardown node in the AST.

        """
        self._add_keyword(node.name)

    def _ignore_bdd_prefixes(self, raw_name: str) -> str:
        """Normalize keyword name by stripping BDD-style prefixes."""
        try:
            parts = raw_name.strip().split(maxsplit=1)
            if len(parts) > 1 and parts[0].lower() in self.bdd_prefixes:
                return parts[1]
        except Exception:
            logger.exception("Error while stripping BDD-style prefix")
            return raw_name
        else:
            return raw_name
