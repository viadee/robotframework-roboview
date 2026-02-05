"""Schemas for keyword similarity functionality."""

from pydantic import BaseModel, Field
from roboview.schemas.domain.keywords import KeywordUsage, SimilarKeyword


class KeywordSimilarityResponse(BaseModel):
    """Response schema for fetching the n most similar keywords for a target keyword."""

    top_n_similar_keywords: list[SimilarKeyword] = Field(description="Top n most similar keywords dictionary")


class DuplicateKeywordResponse(BaseModel):
    """Response schema for fetching all potential duplicate keywords."""

    duplicate_keywords: list[KeywordUsage] = Field(description="List of potential duplicate keywords with usage.")
