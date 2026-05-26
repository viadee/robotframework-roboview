"""Robot parsing model for parsing called keywords in a Robot Framework file."""

import logging

from robot.api.parsing import (
    ModelVisitor,
)
from robot.parsing.model.statements import (
    KeywordCall,
    Setup,
    SuiteSetup,
    SuiteTeardown,
    Teardown,
    TestSetup,
    TestTeardown,
)

logger = logging.getLogger(__name__)

# Built-in keywords that accept a single keyword name as an argument at a fixed position.
# Maps the normalized (lowercase) keyword name to the index of the keyword-name argument.
_BUILTIN_KEYWORD_ARG_INDEX: dict[str, int] = {
    "run keyword": 0,
    "run keyword and continue on failure": 0,
    "run keyword and ignore error": 0,
    "run keyword and return": 0,
    "run keyword and return status": 0,
    "run keyword and warn on failure": 0,
    "run keyword if all tests passed": 0,
    "run keyword if any tests failed": 0,
    "run keyword if test failed": 0,
    "run keyword if test passed": 0,
    "run keyword if timeout occurred": 0,
    "run keyword and expect error": 1,
    "run keyword if": 1,
    "run keyword unless": 1,
    "run keyword and return if": 1,
    "repeat keyword": 1,
    "wait until keyword succeeds": 2,
}


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

    def _strip_library_prefix(self, keyword_name: str) -> str:
        """Strip an optional library or resource prefix from a keyword name.

        Robot Framework only requires a library/resource prefix when there is a
        name collision, so the same keyword may appear with or without a prefix
        and with any library name (not just ``BuiltIn``). Examples:

            * ``Run Keyword``                    -> ``Run Keyword``
            * ``BuiltIn.Run Keyword``            -> ``Run Keyword``
            * ``MyAlias.Run Keyword``            -> ``Run Keyword``
            * ``resources.common.X.Run Keyword`` -> ``Run Keyword``

        Arguments:
            keyword_name (str): The keyword name, optionally prefixed with one or
                more library/resource names separated by dots.

        Returns:
            str: The keyword name without any prefix.

        """
        # rsplit on the LAST dot so nested prefixes are also handled.
        return keyword_name.rsplit(".", 1)[-1]

    def _extract_keyword_arguments(self, keyword_name: str, args: tuple[str, ...]) -> None:
        """Extract keywords passed as arguments to built-in keywords.

        Some Robot Framework built-in keywords accept other keyword names as
        arguments (e.g. ``Wait Until Keyword Succeeds``, ``Run Keyword``).
        This method identifies those cases and adds the embedded keyword names
        to the called_keywords list.

        Arguments:
            keyword_name (str): The name of the called keyword.
            args (tuple[str, ...]): The arguments passed to the keyword.

        """
        try:
            normalized = self._strip_library_prefix(keyword_name).strip().lower()

            # Handle Run Keywords separately: all args (split by AND) are keyword names.
            if normalized == "run keywords":
                self._extract_run_keywords_arguments(args)
                return

            keyword_arg_index = _BUILTIN_KEYWORD_ARG_INDEX.get(normalized)
            if keyword_arg_index is not None and len(args) > keyword_arg_index:
                self._add_keyword(args[keyword_arg_index])
        except Exception:
            logger.exception("Error while extracting keyword arguments from '%s'", keyword_name)

    def _extract_run_keywords_arguments(self, args: tuple[str, ...]) -> None:
        """Extract keyword names from a ``Run Keywords`` call.

        ``Run Keywords`` accepts multiple keyword names separated by ``AND``.
        The first argument and every argument immediately following an ``AND``
        separator is treated as a keyword name.

        Arguments:
            args (tuple[str, ...]): The arguments passed to Run Keywords.

        """
        try:
            if not args:
                return
            # First argument is always a keyword name.
            self._add_keyword(args[0])
            for i, arg in enumerate(args):
                if arg.upper() == "AND" and i + 1 < len(args):
                    self._add_keyword(args[i + 1])
        except Exception:
            logger.exception("Error while extracting Run Keywords arguments")

    def visit_KeywordCall(self, node: KeywordCall) -> None:  # noqa: N802
        """Visit a keyword call and extract the keyword.

        Arguments:
            node (KeywordCall): KeywordCall node in the AST.

        """
        self._add_keyword(node.keyword)
        self._extract_keyword_arguments(node.keyword, node.args)

    def visit_SuiteSetup(self, node: SuiteSetup) -> None:  # noqa: N802
        """Visit a SuiteSetup node and extract the keyword.

        Arguments:
            node (SuiteSetup): SuiteSetup node in the AST.

        """
        self._add_keyword(node.name)
        self._extract_keyword_arguments(node.name, node.args)

    def visit_SuiteTeardown(self, node: SuiteTeardown) -> None:  # noqa: N802
        """Visit a SuiteTeardown node and extract the keyword.

        Arguments:
            node (SuiteTeardown): SuiteTeardown node in the AST.

        """
        self._add_keyword(node.name)
        self._extract_keyword_arguments(node.name, node.args)

    def visit_Setup(self, node: Setup) -> None:  # noqa: N802
        """Visit a Setup node and extract the keyword.

        Arguments:
            node (Setup): Setup node in the AST.

        """
        self._add_keyword(node.name)
        self._extract_keyword_arguments(node.name, node.args)

    def visit_Teardown(self, node: Teardown) -> None:  # noqa: N802
        """Visit a Teardown node and extract the keyword.

        Arguments:
            node (Teardown): Teardown node in the AST.

        """
        self._add_keyword(node.name)
        self._extract_keyword_arguments(node.name, node.args)

    def visit_TestSetup(self, node: TestSetup) -> None:  # noqa: N802
        """Visit a TestSetup node and extract the keyword.

        Arguments:
            node (TestSetup): TestSetup node in the AST.

        """
        self._add_keyword(node.name)
        self._extract_keyword_arguments(node.name, node.args)

    def visit_TestTeardown(self, node: TestTeardown) -> None:  # noqa: N802
        """Visit a TestTeardown node and extract the keyword.

        Arguments:
            node (TestTeardown): TestTeardown node in the AST.

        """
        self._add_keyword(node.name)
        self._extract_keyword_arguments(node.name, node.args)

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
