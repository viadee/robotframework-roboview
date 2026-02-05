"""Service class implementing the keyword usage functionality."""

import logging
from pathlib import Path

from roboview.registries.file_registry import FileRegistry
from roboview.registries.keyword_registry import KeywordRegistry
from roboview.schemas.domain.common import FileType, KeywordType
from roboview.schemas.domain.files import FileUsage
from roboview.schemas.domain.keywords import KeywordUsage
from roboview.services.keyword_similarity_service import KeywordSimilarityService

logger = logging.getLogger(__name__)


class KeywordUsageService:
    """Class to provide the Keyword usage functionality."""

    def __init__(self, keyword_registry: KeywordRegistry, file_registry: FileRegistry) -> None:
        """Initialize KeywordUsageService.

        Arguments:
            keyword_registry (KeywordRegistry): Initialized keyword registry object.
            file_registry (FileRegistry): Initialized file registry object.


        Attributes:
            keyword_registry (KeywordRegistry): Initialized keyword registry object.
            file_registry (FileRegistry): Initialized file registry object.

        """
        self.keyword_registry = keyword_registry
        self.file_registry = file_registry

    def get_keywords_with_global_usage_for_file(self, file_path: Path, keyword_type: KeywordType) -> list[KeywordUsage]:
        """Get initialized or called keywords with global usage for a Robot Framework file.

        Arguments:
            file_path (str): Path of the file to analyze.
            keyword_type (KeywordType): Flag to indicate if called or initialized keywords are requested.


        Returns:
            list: List of dictionaries containing keyword information and usage counts.

        """
        try:
            result = []

            if keyword_type is KeywordType.INITIALIZED:
                requested_keywords = self._get_init_keywords_for_file(file_path.as_posix())
            else:
                requested_keywords = self._get_called_keywords_for_file(file_path.as_posix())

            for kw in requested_keywords:
                if not isinstance(kw, str):
                    continue

                try:
                    keyword = self.keyword_registry.resolve(kw)

                    if keyword:
                        result.append(
                            KeywordUsage(
                                keyword_id=keyword.keyword_id,
                                file_name=keyword.file_name,
                                keyword_name_without_prefix=keyword.keyword_name_without_prefix,
                                keyword_name_with_prefix=keyword.keyword_name_with_prefix,
                                documentation=keyword.description,
                                source=keyword.source,
                                file_usages=self._get_keyword_usage_for_target_keyword_in_file(
                                    kw, file_path.as_posix()
                                ),
                                total_usages=self._get_global_keyword_usage_for_target_keyword(kw),
                            )
                        )
                except Exception:
                    logger.exception("Failed to process keyword '%s'", kw)
                    continue

        except Exception:
            logger.exception("Failed to get keywords with global usage for file '%s'", file_path)
            return []
        else:
            return result

    def get_keyword_usage_in_files_for_target_keyword(self, keyword_name: str, file_type: FileType) -> list[FileUsage]:
        """Get file names and usage counts for a target keyword in resource or robot files.

        Args:
            keyword_name (str): The keyword name to get file names and usages for.
            file_type (FileType): Whether to search in RESOURCE or ROBOT files.

        Returns:
            list: List of dictionaries containing file names and usage counts.

        """
        try:
            keyword = self.keyword_registry.resolve(keyword_name)

            if keyword is None:
                logger.warning("Keyword '%s' not found in registry", keyword_name)
                return []

            unique_keyword_names = {
                keyword.keyword_name_without_prefix,
                keyword.keyword_name_with_prefix,
            }

            result = []
            for entry in self.file_registry.get_all_files():
                try:
                    if entry.is_resource != bool(file_type is FileType.RESOURCE):
                        continue

                    if not entry.called_keywords:
                        continue

                    count = sum(entry.called_keywords.count(k) for k in unique_keyword_names)

                    if count:
                        result.append(
                            FileUsage(
                                file_name=entry.file_name,
                                path=entry.path,
                                usages=count,
                            )
                        )
                except Exception:
                    logger.exception(
                        "Failed to process file entry '%s'", entry.path if hasattr(entry, "path") else "unknown"
                    )
                    continue

        except Exception:
            logger.exception("Failed to get keyword usage in files for keyword '%s'", keyword_name)
            return []
        else:
            return result

    def get_keywords_without_documentation(self) -> list[KeywordUsage]:
        """Return all keywords that have no [Documentation].

        Returns:
            list[dict]: List of dictionaries containing keywords without documentation.

        """
        try:
            result = []
            for entry in self.keyword_registry.get_all_keywords():
                if not entry.description:
                    try:
                        result.append(
                            KeywordUsage(
                                keyword_id=entry.keyword_id,
                                file_name=entry.file_name,
                                keyword_name_without_prefix=entry.keyword_name_without_prefix,
                                keyword_name_with_prefix=entry.keyword_name_with_prefix,
                                documentation=entry.description,
                                source=entry.source,
                                file_usages=self._get_keyword_usage_for_target_keyword_in_file(
                                    entry.keyword_name_with_prefix, entry.source
                                ),
                                total_usages=self._get_global_keyword_usage_for_target_keyword(
                                    entry.keyword_name_with_prefix
                                ),
                            )
                        )
                    except Exception:
                        logger.exception("Failed to process keyword '%s'", entry.keyword_name_with_prefix)
                        continue
        except Exception:
            logger.exception("Failed to get keywords without documentation")
            return []
        else:
            return result

    def get_keywords_without_usages(self) -> list[KeywordUsage]:
        """Return all keywords that have no usages across the whole project.

        Returns:
            list[dict]: List of dictionaries containing keywords that have no usages in the project.

        """
        try:
            keywords_wo_usages = []
            for entry in self.keyword_registry.get_user_defined_keywords():
                try:
                    total_usages = self._get_global_keyword_usage_for_target_keyword(entry.keyword_name_with_prefix)
                    if total_usages == 0:
                        keywords_wo_usages.append(
                            KeywordUsage(
                                keyword_id=entry.keyword_id,
                                file_name=entry.file_name,
                                keyword_name_without_prefix=entry.keyword_name_without_prefix,
                                keyword_name_with_prefix=entry.keyword_name_with_prefix,
                                documentation=entry.description,
                                source=entry.source,
                                file_usages=total_usages,
                                total_usages=total_usages,
                            )
                        )
                except Exception:
                    logger.exception("Failed to process keyword '%s'", entry.keyword_name_with_prefix)
                    continue
        except Exception:
            logger.exception("Failed to get keywords without usages")
            return []
        else:
            return keywords_wo_usages

    def get_potential_duplicate_keywords(self, keyword_sim_service: KeywordSimilarityService) -> list[KeywordUsage]:
        """Return keywords that have calling cycles along their usages.

        Arguments:
            keyword_sim_service: KeywordSimilarityService instance.

        Returns:
            list[KeywordUsage]: List of KeywordUsage objects containing keywords that are potential duplicate keywords.

        """
        try:
            keyword_props_list = keyword_sim_service.get_all_similar_keywords_above_threshold()

            result = []
            for entry in keyword_props_list:
                if entry is None:
                    continue
                try:
                    result.append(
                        KeywordUsage(
                            keyword_id=entry.keyword_id,
                            file_name=entry.file_name,
                            keyword_name_without_prefix=entry.keyword_name_without_prefix,
                            keyword_name_with_prefix=entry.keyword_name_with_prefix,
                            documentation=entry.description,
                            source=entry.source,
                            file_usages=self._get_keyword_usage_for_target_keyword_in_file(
                                entry.keyword_name_with_prefix, entry.source
                            ),
                            total_usages=self._get_global_keyword_usage_for_target_keyword(
                                entry.keyword_name_with_prefix
                            ),
                        )
                    )
                except Exception:
                    logger.exception(
                        "Failed to process keyword '%s'",
                        entry.keyword_name_with_prefix if hasattr(entry, "keyword_name_with_prefix") else "unknown",
                    )
                    continue
        except Exception:
            logger.exception("Failed to get potential duplicate keywords")
            return []
        else:
            return result

    def get_keyword_reusage_rate(self) -> float:
        """Return the keyword reusage rate as number between 0 and 1."""
        try:
            keyword_props = self._get_user_defined_keywords_with_usages()
            if not keyword_props:
                logger.warning("No user-defined keywords found for reusage rate calculation")
                return 0.0
            num_user_defined_keywords_with_count_greater_one = sum(1 for ku in keyword_props if ku.total_usages > 1)
            return round((num_user_defined_keywords_with_count_greater_one / len(keyword_props)), 2)
        except ZeroDivisionError:
            logger.warning("Division by zero in keyword reusage rate calculation")
            return 0.0
        except Exception:
            logger.exception("Failed to calculate keyword reusage rate")
            return 0.0

    def get_documentation_coverage(self) -> float:
        """Return the ratio of keywords that have [Documentation] across the whole project."""
        try:
            user_defined_keywords = self.keyword_registry.get_user_defined_keywords()
            if not user_defined_keywords:
                logger.warning("No user-defined keywords found for documentation coverage calculation")
                return 0.0
            keywords_without_docs = self.get_keywords_without_documentation()
            return round(1 - (len(keywords_without_docs) / len(user_defined_keywords)), 2)
        except ZeroDivisionError:
            logger.warning("Division by zero in documentation coverage calculation")
            return 0.0
        except Exception:
            logger.exception("Failed to calculate documentation coverage")
            return 0.0

    def get_most_used_user_defined_keywords(self, top_n: int) -> list[KeywordUsage]:
        """Return the top n most used user defined keywords in the project."""
        try:
            keywords = self._get_user_defined_keywords_with_usages()
            return sorted(keywords, key=lambda ku: ku.total_usages, reverse=True)[:top_n]
        except Exception:
            logger.exception("Failed to get most used user defined keywords")
            return []

    def get_most_used_external_or_builtin_keywords(self, top_n: int) -> list[KeywordUsage]:
        """Return the top n most used external or builtin keywords in the project."""
        try:
            keywords = self._get_external_or_builtin_keywords_with_usages()
            return sorted(keywords, key=lambda ku: ku.total_usages, reverse=True)[:top_n]
        except Exception:
            logger.exception("Failed to get most used external or builtin keywords")
            return []

    def _get_external_or_builtin_keywords_with_usages(self) -> list[KeywordUsage]:
        """Return all external or builtin keywords with their usage count.

        Returns:
            list[KeywordUsage]: List of KeywordUsage objects containing keywords along their usages.

        """
        try:
            keyword_props_list = self.keyword_registry.get_non_user_defined_keywords()

            result = []
            for entry in keyword_props_list:
                if entry is None:
                    continue
                try:
                    result.append(
                        KeywordUsage(
                            keyword_id=entry.keyword_id,
                            file_name=entry.file_name,
                            keyword_name_without_prefix=entry.keyword_name_without_prefix,
                            keyword_name_with_prefix=entry.keyword_name_with_prefix,
                            documentation=entry.description,
                            source=entry.source,
                            file_usages=self._get_keyword_usage_for_target_keyword_in_file(
                                entry.keyword_name_with_prefix, entry.source
                            ),
                            total_usages=self._get_global_keyword_usage_for_target_keyword(
                                entry.keyword_name_with_prefix
                            ),
                        )
                    )
                except Exception:
                    logger.exception(
                        "Failed to process keyword '%s'",
                        entry.keyword_name_with_prefix if hasattr(entry, "keyword_name_with_prefix") else "unknown",
                    )
                    continue
        except Exception:
            logger.exception("Failed to get external or builtin keywords with usages")
            return []
        else:
            return result

    def _get_user_defined_keywords_with_usages(self) -> list[KeywordUsage]:
        """Return all keywords with their usage count.

        Returns:
            list[KeywordUsage]: List of KeywordUsage objects containing keywords along their usages.

        """
        try:
            keyword_props_list = self.keyword_registry.get_user_defined_keywords()

            result = []
            for entry in keyword_props_list:
                try:
                    result.append(
                        KeywordUsage(
                            keyword_id=entry.keyword_id,
                            file_name=entry.file_name,
                            keyword_name_without_prefix=entry.keyword_name_without_prefix,
                            keyword_name_with_prefix=entry.keyword_name_with_prefix,
                            documentation=entry.description,
                            source=entry.source,
                            file_usages=self._get_keyword_usage_for_target_keyword_in_file(
                                entry.keyword_name_with_prefix, entry.source
                            ),
                            total_usages=self._get_global_keyword_usage_for_target_keyword(
                                entry.keyword_name_with_prefix
                            ),
                        )
                    )
                except Exception:
                    logger.exception("Failed to process keyword '%s'", entry.keyword_name_with_prefix)
                    continue
        except Exception:
            logger.exception("Failed to get user defined keywords with usages")
            return []
        else:
            return result

    def _get_init_keywords_for_file(self, file_path: str) -> list[str]:
        """Get initialized keywords for a Robot Framework file.

        Arguments:
            file_path (str): Path of the file to fetch initialized keywords from.

        Returns:
            list: List of initialized keywords for the target file.

        """
        try:
            for entry in self.file_registry.get_all_files():
                if entry.path == file_path:
                    return entry.initialized_keywords or []
        except Exception:
            logger.exception("Failed to get initialized keywords for file '%s'", file_path)
            return []
        else:
            return []

    def _get_called_keywords_for_file(self, file_path: str) -> list[str]:
        """Get called keywords for a Robot Framework file.

        Arguments:
            file_path (str): Path of the file to fetch initialized keywords from.

        Returns:
            list: List of called keywords for the target file.

        """
        try:
            for entry in self.file_registry.get_all_files():
                if entry.path == file_path:
                    return entry.called_keywords or []
        except Exception:
            logger.exception("Failed to get called keywords for file '%s'", file_path)
            return []
        else:
            return []

    def _get_keyword_usage_for_target_keyword_in_file(self, keyword_name: str, file_path: str) -> int:
        """Calculate how often a keyword is used in a specific Robot Framework file.

        Arguments:
            keyword_name (str): The keyword name.
            file_path (str): Path of the file to count the keyword usages from.

        Returns:
            int: Count how often a keyword is used in the requested file.

        """
        try:
            keyword = self.keyword_registry.resolve(keyword_name)

            if keyword is None:
                return 0

            for entry in self.file_registry.get_all_files():
                if entry.path == file_path:
                    called_keywords = entry.called_keywords
                    if called_keywords is None:
                        return 0
                    return called_keywords.count(keyword.keyword_name_with_prefix) + called_keywords.count(
                        keyword.keyword_name_without_prefix
                    )
        except Exception:
            logger.exception("Failed to get keyword usage for '%s' in file '%s'", keyword_name, file_path)
            return 0
        else:
            return 0

    def _get_global_keyword_usage_for_target_keyword(self, keyword_name: str) -> int:
        """Calculate the global keyword usages count for a target keyword across the whole project.

        Arguments:
            keyword_name (str): Name of the keyword.

        Returns:
            int: Total usage count for the target keyword across the project.

        """
        try:
            keyword = self.keyword_registry.resolve(keyword_name)

            if keyword is None:
                return 0

            total_usage = 0
            unique_keyword_names = {keyword.keyword_name_without_prefix, keyword.keyword_name_with_prefix}
            for entry in self.file_registry.get_all_files():
                try:
                    called_keywords = entry.called_keywords
                    if called_keywords is None:
                        continue
                    count = sum(called_keywords.count(k) for k in unique_keyword_names)
                    if count > 0:
                        total_usage += count
                except Exception:
                    logger.exception("Failed to process file entry for global keyword usage")
                    continue

        except Exception:
            logger.exception("Failed to get global keyword usage for '%s'", keyword_name)
            return 0
        else:
            return total_usage
