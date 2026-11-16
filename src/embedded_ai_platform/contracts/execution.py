"""Execution contracts shared by the platform and its agents."""

from datetime import datetime
from enum import StrEnum
from typing import Generic, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

from embedded_ai_platform.contracts.errors import ErrorInfo

OutputT = TypeVar("OutputT", bound=BaseModel)


class ExecutionStatus(StrEnum):
    """Lifecycle states of an agent execution."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMED_OUT = "timed_out"


class ExecutionResult(BaseModel, Generic[OutputT]):
    """Structured execution state and result."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    execution_id: str = Field(min_length=1)
    agent_id: str = Field(min_length=1)
    status: ExecutionStatus
    output: OutputT | None = None
    error: ErrorInfo | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @field_validator("started_at", "completed_at")
    @classmethod
    def validate_timezone_aware(cls, value: datetime | None) -> datetime | None:
        """Require timestamps to include timezone information."""

        if value is not None and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("Execution timestamps must be timezone-aware.")

        return value

    @model_validator(mode="after")
    def validate_execution_state(self) -> "ExecutionResult[OutputT]":
        """Prevent contradictory execution states and result fields."""

        if self.status == ExecutionStatus.PENDING:
            if any(
                value is not None
                for value in (
                    self.output,
                    self.error,
                    self.started_at,
                    self.completed_at,
                )
            ):
                raise ValueError("PENDING execution cannot contain results or timestamps.")

        elif self.status == ExecutionStatus.RUNNING:
            if self.started_at is None:
                raise ValueError("RUNNING execution requires started_at.")

            if self.completed_at is not None:
                raise ValueError("RUNNING execution cannot have completed_at.")

            if self.output is not None or self.error is not None:
                raise ValueError("RUNNING execution cannot contain a final result or error.")

        elif self.status == ExecutionStatus.SUCCEEDED:
            if self.output is None:
                raise ValueError("SUCCEEDED execution requires output.")

            if self.error is not None:
                raise ValueError("SUCCEEDED execution cannot contain an error.")

            if self.started_at is None or self.completed_at is None:
                raise ValueError("SUCCEEDED execution requires both timestamps.")

        elif self.status == ExecutionStatus.FAILED:
            if self.error is None:
                raise ValueError("FAILED execution requires an error.")

            if self.output is not None:
                raise ValueError("FAILED execution cannot contain output.")

            if self.started_at is None or self.completed_at is None:
                raise ValueError("FAILED execution requires both timestamps.")

        elif self.status in (
            ExecutionStatus.CANCELLED,
            ExecutionStatus.TIMED_OUT,
        ):
            if self.output is not None:
                raise ValueError(f"{self.status.value.upper()} execution cannot contain output.")

            if self.completed_at is None:
                raise ValueError(f"{self.status.value.upper()} execution requires completed_at.")

            if self.status == ExecutionStatus.TIMED_OUT and self.started_at is None:
                raise ValueError("TIMED_OUT execution requires started_at.")

        if (
            self.started_at is not None
            and self.completed_at is not None
            and self.completed_at < self.started_at
        ):
            raise ValueError("completed_at cannot precede started_at.")

        return self
