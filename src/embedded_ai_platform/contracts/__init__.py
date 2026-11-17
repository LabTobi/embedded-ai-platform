"""Public contracts for the Embedded AI Platform."""

from embedded_ai_platform.contracts.agent import Agent
from embedded_ai_platform.contracts.context import (
    CancellationToken,
    ExecutionContext,
)
from embedded_ai_platform.contracts.errors import ErrorCategory, ErrorInfo
from embedded_ai_platform.contracts.execution import ExecutionResult, ExecutionStatus

__all__ = [
    "Agent",
    "CancellationToken",
    "ErrorCategory",
    "ErrorInfo",
    "ExecutionContext",
    "ExecutionResult",
    "ExecutionStatus",
]
