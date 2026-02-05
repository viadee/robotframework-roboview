"""Domain robocop schema for pydantic validation."""

from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field


class RuleCategory(Enum):
    """Enum to categorize Robocop error messages.

    See https://robocop.dev/stable/rules_list/ for more detailed information.

    """

    ARG = "Arguments"
    COM = "Comments"
    DEPR = "Deprecated"
    DOC = "Documentation"
    DUP = "Duplication"
    ERR = "Errors"
    IMP = "Imports"
    KW = "Keywords"
    LEN = "Lengths"
    MISC = "Miscellaneous"
    NAME = "Naming"
    ORD = "Order"
    SPC = "Spacing"
    TAG = "Tags"
    VAR = "Variables"
    ANN = "Annotations"


class RobocopMessage(BaseModel):
    """Schema containing Robocop message properties."""

    message_id: str = Field(
        description="Unique identifier for the specific Robocop error message", default_factory=lambda: str(uuid4())
    )
    rule_id: str = Field(description="Rule identifier of the corresponding rule")
    rule_message: str = Field(description="The general rule message")
    message: str = Field(description="Detailed description of the corresponding rule")
    category: str | RuleCategory = Field(description="Category of the corresponding rule")
    file_name: str = Field(description="File name of where the error occurred")
    source: str = Field(description="File path of where the error occurred as POSIX")
    severity: str = Field(description="Severity of the corresponding rule e.g INFO, WARNING, ERROR")
    code: str = Field(description="Code snippet, where the error stems from")


class IssueSummary(BaseModel):
    """Schema containing an robocop error issue summary."""

    category: str | RuleCategory = Field(description="Category of the corresponding rule")
    count: int = Field(description="Count of errors with this exact rule")
