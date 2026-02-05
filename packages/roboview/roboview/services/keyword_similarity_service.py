"""Functionality to cover the KeywordSimilarity."""

import logging

import numpy as np
from pygments import lex
from pygments.lexers import get_lexer_by_name
from roboview.registries.keyword_registry import KeywordRegistry
from roboview.schemas.domain.keywords import KeywordProperties, SimilarKeyword
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class KeywordSimilarityService:
    """Class for calculating and querying the similarity between Keywords.

    This class provides functionality to analyze keyword similarity across Robot Framework
    files using TF-IDF vectorization and cosine similarity metrics. It can identify
    similar keywords based on their source code structure and content.

    Attributes:
        keyword_registry (KeywordRegistry): Initialized KeywordRegistry object.
        keyword_names_list: List containing all keyword names.
        similarity_matrix: Similarity matrix containing all keyword similarity scores.

    """

    def __init__(self, keyword_registry: KeywordRegistry) -> None:
        """Initialize KeywordSimilarity with a project directory path.

        Arguments:
            keyword_registry (KeywordRegistry): Initialized KeywordRegistry object.

        """
        self.keyword_registry = keyword_registry
        self.keyword_names_list = []
        self.similarity_matrix: np.ndarray = np.array([])

    def calculate_keyword_similarity_matrix(self) -> None:
        """Calculate the keyword similarity matrix using TF-IDF and cosine similarity.

        Analyzes keyword source code to compute similarity scores between all keywords
        in the project using tokenization and vectorization techniques.

        Raises:
            Exception: Logs errors during tokenization, vectorization, or similarity calculation.

        """
        try:
            keywords = self.keyword_registry.get_user_defined_keywords()

            if len(keywords) == 0:
                logger.warning("No keywords found. Similarity matrix cannot be computed.")
                return

            keyword_names_list = [k.keyword_name_with_prefix for k in keywords]
            keyword_code_list = [k.code for k in keywords]

            # Tokenize keyword source code
            try:
                lexer = get_lexer_by_name("text")
                tokenized_keywords = []

                for keyword_code in keyword_code_list:
                    try:
                        tokens = [token[1] for token in lex(keyword_code, lexer) if token[1].strip()]
                        tokenized_keywords.append(" ".join(tokens))
                    except Exception:
                        logger.exception("Failed to tokenize keyword: %s", keyword_code)
                        tokenized_keywords.append(keyword_code)
            except Exception:
                logger.exception("Failed to initialize lexer or tokenize keywords")
                return

            # Create similarity matrix
            try:
                vectorizer = CountVectorizer()
                vectors = vectorizer.fit_transform(tokenized_keywords)
                similarity_matrix = cosine_similarity(vectors)
            except Exception:
                logger.exception("Failed to create vectors or calculate similarity matrix")
                return
            else:
                self.similarity_matrix = similarity_matrix
                self.keyword_names_list = keyword_names_list

        except Exception:
            logger.exception("Unexpected error during similarity matrix calculation")
            return

    def get_n_most_similar_keywords(self, keyword_name: str, top_n: int) -> list[SimilarKeyword]:  # noqa: C901
        """Return the n most similar keywords from the similarity matrix.

        Arguments:
            keyword_name (str): The target keyword to find similarities for.
            top_n (int): The number of similar keywords to return.

        Returns:
            dict[str, str | dict[str, float]]: Dictionary containing:
                - 'keyword': The target keyword name
                - 'similar_keywords': Dict mapping similar keyword names to similarity scores

            Returns empty similar_keywords dict if keyword not found or on error.

        """
        if not keyword_name:
            logger.warning("Empty keyword provided to get_n_most_similar_keywords")
            return []

        keyword = self.keyword_registry.resolve(keyword_name)

        if not keyword:
            logger.warning("Keyword not found in similarity matrix")
            return []

        try:
            index = self.keyword_names_list.index(keyword.keyword_name_with_prefix)
        except ValueError:
            logger.warning("Keyword '%s' not found in keyword list", keyword_name)
            return []

        try:
            similarities = self.similarity_matrix[index]
            similar_indices = np.argsort(similarities)[::-1]

            similar_keywords = []
            for i in similar_indices:
                if i == index:
                    continue

                try:
                    similarity_score = round(float(similarities[i]), 4)
                    entry = self.keyword_registry.resolve(self.keyword_names_list[i])

                    if entry is None:
                        continue

                    similar_keywords.append(
                        SimilarKeyword(
                            keyword_id=entry.keyword_id,
                            keyword_name_without_prefix=entry.keyword_name_without_prefix,
                            keyword_name_with_prefix=entry.keyword_name_with_prefix,
                            source=entry.source,
                            score=similarity_score,
                        )
                    )
                    if len(similar_keywords) >= top_n:
                        break
                except (IndexError, ValueError):
                    logger.exception("Invalid index or similarity score at position %d", i)
                    continue

        except (IndexError, ValueError):
            logger.exception("Error accessing similarity matrix for keyword: %s", keyword_name)
            return []
        except Exception:
            logger.exception("Unexpected error while finding similar keywords for: %s", keyword_name)
            return []
        else:
            return similar_keywords

    def get_all_similar_keywords_above_threshold(self, threshold: float = 0.80) -> list[KeywordProperties | None]:
        """Return all keywords that have at least one similarity score above the given threshold.

        Arguments:
            threshold (float): Minimum similarity score (default: 0.80).

        Returns:
            list: List of keywords that have high similarity with at least one other keyword.

        """
        if self.similarity_matrix.size == 0:
            logger.warning("Similarity matrix is empty")
            return []

        try:
            similar_keyword_indices = set()
            n = len(self.keyword_names_list)

            for i in range(n):
                for j in range(i + 1, n):
                    similarity_score = round(float(self.similarity_matrix[i, j]), 4)
                    if similarity_score >= threshold:
                        similar_keyword_indices.add(i)
                        similar_keyword_indices.add(j)

            similar_keywords = []
            for idx in sorted(similar_keyword_indices):
                try:
                    keyword = self.keyword_registry.resolve(self.keyword_names_list[idx])
                    if keyword:
                        similar_keywords.append(keyword)
                except (AttributeError, ValueError, IndexError):
                    logger.exception("Error resolving keyword at position %d", idx)
                    continue

        except Exception:
            logger.exception("Unexpected error while finding similar keywords")
            return []

        return similar_keywords
