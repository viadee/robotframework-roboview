"""Robocop schemas for pydantic validation."""

from pydantic import BaseModel, Field
from roboview.schemas.domain.robocop import RobocopMessage


class RobocopMessageResponse(BaseModel):
    """Response schema for a single Robocop message."""

    message: RobocopMessage = Field(description=" Single Robocop message")


class RobocopMessagesResponse(BaseModel):
    """Response schema for a list of Robocop messages."""

    messages: list[RobocopMessage] = Field(description=" Single Robocop message")


class RobocopMessagesByCategoryResponse(BaseModel):
    """Response schema for a list of Robocop messages filtered by category."""

    messages_by_category: list[RobocopMessage] = Field(description=" Single Robocop message")
