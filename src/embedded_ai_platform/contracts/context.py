"""Execution context contracts."""

from logging import Logger
from typing import Protocol


class CancellationToken(Protocol):
    """Read-only interface for cooperative cancellation."""

    @property
    def cancelled(self) -> bool:
        """Whether cancellation has been requested."""
        ...

    async def wait(self) -> None:
        """Wait until cancellation is requested."""
        ...


class ExecutionContext(Protocol):
    """Read-only context provided by the runtime to an agent."""

    @property
    def execution_id(self) -> str:
        """Unique execution identifier."""
        ...

    @property
    def agent_id(self) -> str:
        """Identifier of the executing agent."""
        ...

    @property
    def cancellation_token(self) -> CancellationToken:
        """Cooperative cancellation interface."""
        ...

    @property
    def deadline(self) -> float | None:
        """Absolute deadline based on the monotonic clock."""
        ...

    @property
    def logger(self) -> Logger:
        """Execution-scoped logger."""
        ...

    @property
    def trace_id(self) -> str | None:
        """Distributed tracing identifier, if available."""
        ...
