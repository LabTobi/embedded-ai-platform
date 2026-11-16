"""Shared error contracts for agent execution."""

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, JsonValue


class ErrorCategory(StrEnum):
    """High-level categories used to classify execution errors."""

    INPUT = "input"
    AGENT = "agent"
    TOOL = "tool"
    PROVIDER = "provider"
    RUNTIME = "runtime"
    SYSTEM = "system"


class ErrorInfo(BaseModel):
    """Structured, JSON-compatible information about an execution error.

    The producer is responsible for sanitizing details and ensuring
    that no secrets or sensitive information are included.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    category: ErrorCategory
    code: str = Field(min_length=1)
    message: str = Field(min_length=1)
    retryable: bool = False
    details: dict[str, JsonValue] = Field(default_factory=dict)
