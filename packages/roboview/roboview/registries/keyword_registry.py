"""Keyword registry for centralized keyword lookup and management."""

import logging

from roboview.schemas.domain.keywords import KeywordProperties

logger = logging.getLogger(__name__)


class KeywordRegistry:
    """Central registry for keyword lookup and resolution.

    This class provides a centralized store for all keywords in a Robot Framework
    project, including local keywords from .robot and .resource files, as well as
    external library keywords e.g Browser.

    The registry supports lookup by both prefixed and unprefixed keyword names,
    enabling resolution of keyword calls with adherence to the Robot Framework definitions.

    Attributes:
        _keyword_registry: Dictionary containing all registered keywords.

    """

    def __init__(self) -> None:
        """Initialize an empty keyword registry."""
        self._keyword_registry: dict[str, KeywordProperties] = {}

    def register(self, keyword: KeywordProperties) -> None:
        """Register a keyword in the registry.

        Arguments:
            keyword: The keyword to register.

        """
        try:
            self._keyword_registry[keyword.keyword_id] = keyword

        except Exception:
            logger.exception("Failed to register keyword: %s", keyword.keyword_name_without_prefix)

    def resolve(self, keyword_name: str) -> KeywordProperties | None:
        """Resolve a keyword name to its keyword properties object.

        Supports lookup by both prefixed and unprefixed names.

        Arguments:
            keyword_name: The keyword name to resolve (with or without prefix).

        Returns:
            KeywordProperties: Keyword properties object if found, None otherwise.

        """
        if not keyword_name:
            logger.warning("Empty keyword_name provided to resolve()")
            return None

        normalized = self._normalize_keyword_name(keyword_name)

        try:
            if result := next(
                (kw for kw in self.get_all_keywords() if kw.validation_str_with_prefix == normalized),
                None,
            ):
                return result

            if result := next(
                (kw for kw in self.get_all_keywords() if kw.validation_str_without_prefix == normalized),
                None,
            ):
                return result

        except Exception:
            logger.exception("Error while resolving keyword: %s", keyword_name)
            return None
        else:
            return None

    def get_prefix_variants(self, keyword_name: str) -> tuple[str, str]:
        """Get both prefix variants of a keyword name.

        Arguments:
            keyword_name: The keyword name to look up (with or without prefix).

        Returns:
            Tuple of (keyword_with_prefix, keyword_without_prefix).
            If keyword is not found, returns (keyword_name, keyword_name).

        """
        if not keyword_name:
            logger.warning("Empty keyword_name provided to get_prefix_variants()")
            return keyword_name, keyword_name

        try:
            metadata = self.resolve(keyword_name)

            if metadata:
                return (
                    metadata.keyword_name_with_prefix or metadata.keyword_name_without_prefix,
                    metadata.keyword_name_without_prefix,
                )

        except Exception:
            logger.exception("Error while getting prefix variants for: %s", keyword_name)
            raise
        else:
            logger.warning("Keyword not found in registry: %s", keyword_name)
            return keyword_name, keyword_name

    def get_all_keywords(self) -> list[KeywordProperties]:
        """Get all registered keywords.

        Returns:
            List of all keyword metadata in the registry.

        """
        return list(self._keyword_registry.values())

    def get_user_defined_keywords(self) -> list[KeywordProperties]:
        """Get all user defined keywords.

        Returns:
            List of all user defined keyword metadata in the registry.

        """
        return [keyword_props for keyword_props in self._keyword_registry.values() if keyword_props.is_user_defined]

    def get_non_user_defined_keywords(self) -> list[KeywordProperties]:
        """Get all external or BuiltIn keywords.

        Returns:
            List of all browser keyword metadata in the registry.

        """
        return [keyword_props for keyword_props in self._keyword_registry.values() if not keyword_props.is_user_defined]

    @staticmethod
    def _normalize_keyword_name(keyword_name: str) -> str:
        """Normalize a keyword name for existence validation."""
        return keyword_name.lower().replace(" ", "").replace("_", "")

    def clear(self) -> None:
        """Clear all registered keywords."""
        self._keyword_registry.clear()

    def __len__(self) -> int:
        """Return the number of registered keywords."""
        return len(self._keyword_registry)

    def __contains__(self, keyword_name: str) -> bool:
        """Check if a keyword is registered."""
        return self.resolve(keyword_name) is not None
