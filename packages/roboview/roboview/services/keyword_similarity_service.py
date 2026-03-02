"""Functionality to cover the KeywordSimilarity."""

import logging
from collections import Counter
from math import sqrt

from pygments import lex
from pygments.lexers import get_lexer_by_name
from roboview.registries.keyword_registry import KeywordRegistry
from roboview.schemas.domain.keywords import KeywordProperties, SimilarKeyword

logger = logging.getLogger(__name__)


class KeywordSimilarityService:
    """Class for calculating and querying the similarity between Keywords.

    This class provides functionality to analyze keyword similarity across Robot Framework
    files using token frequency vectors and cosine similarity metrics. It can identify
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
        self.similarity_matrix: list[list[float]] = []

    @staticmethod
    def _calculate_cosine_similarity(
        vector_a: Counter[str],
        vector_b: Counter[str],
        norm_a: float,
        norm_b: float,
    ) -> float:
        """Calculate cosine similarity for two sparse token vectors.

        Arguments:
            vector_a (Counter[str]): Sparse token frequency vector for the first keyword.
            vector_b (Counter[str]): Sparse token frequency vector for the second keyword.
            norm_a (float): Precomputed Euclidean norm of vector_a.
            norm_b (float): Precomputed Euclidean norm of vector_b.

        Returns:
            float: Cosine similarity score in range [0.0, 1.0]. Returns 0.0 if one
                of the vectors has a zero norm.

        """
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0

        if len(vector_a) > len(vector_b):
            vector_a, vector_b = vector_b, vector_a

        dot_product = sum(value * vector_b.get(token, 0) for token, value in vector_a.items())
        return dot_product / (norm_a * norm_b)

    def _build_similarity_matrix(self, tokenized_keywords: list[str]) -> list[list[float]]:
        """Build a full pairwise similarity matrix for tokenized keywords.

        Arguments:
            tokenized_keywords (list[str]): List of whitespace-separated token strings,
                one entry per keyword.

        Returns:
            list[list[float]]: Symmetric cosine similarity matrix where matrix[i][j]
                represents the similarity between keyword i and keyword j.

        """
        token_vectors = [Counter(tokens.split()) for tokens in tokenized_keywords]
        norms = [sqrt(sum(value * value for value in token_vector.values())) for token_vector in token_vectors]

        vector_count = len(token_vectors)
        similarity_matrix = [[0.0] * vector_count for _ in range(vector_count)]

        for i in range(vector_count):
            similarity_matrix[i][i] = 1.0
            for j in range(i + 1, vector_count):
                similarity = self._calculate_cosine_similarity(
                    token_vectors[i],
                    token_vectors[j],
                    norms[i],
                    norms[j],
                )
                similarity_matrix[i][j] = similarity
                similarity_matrix[j][i] = similarity

        return similarity_matrix

    def calculate_keyword_similarity_matrix(self) -> None:
        """Calculate the keyword similarity matrix using token vectors and cosine similarity.

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
                similarity_matrix = self._build_similarity_matrix(tokenized_keywords)
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
            similar_indices = sorted(
                range(len(similarities)),
                key=lambda similarity_index: similarities[similarity_index],
                reverse=True,
            )

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
        if not self.similarity_matrix:
            logger.warning("Similarity matrix is empty")
            return []

        try:
            similar_keyword_indices = set()
            n = len(self.keyword_names_list)

            for i in range(n):
                for j in range(i + 1, n):
                    similarity_score = round(float(self.similarity_matrix[i][j]), 4)
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
