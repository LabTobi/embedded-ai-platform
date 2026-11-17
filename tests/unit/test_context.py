"""Unit tests for execution context contracts."""

import asyncio
from logging import Logger, getLogger

from embedded_ai_platform.contracts.context import (
    CancellationToken,
    ExecutionContext,
)


class FakeCancellationToken:
    """Test implementation of CancellationToken."""

    def __init__(self) -> None:
        self._event = asyncio.Event()

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    async def wait(self) -> None:
        await self._event.wait()

    def cancel(self) -> None:
        self._event.set()


class FakeExecutionContext:
    """Test implementation of ExecutionContext."""

    def __init__(self) -> None:
        self._token = FakeCancellationToken()
        self._logger = getLogger("tests.execution")

    @property
    def execution_id(self) -> str:
        return "exec-test-001"

    @property
    def agent_id(self) -> str:
        return "test-agent"

    @property
    def cancellation_token(self) -> CancellationToken:
        return self._token

    @property
    def deadline(self) -> float | None:
        return None

    @property
    def logger(self) -> Logger:
        return self._logger

    @property
    def trace_id(self) -> str | None:
        return "trace-test-001"


def test_execution_context_structural_typing() -> None:
    context: ExecutionContext = FakeExecutionContext()

    assert context.execution_id == "exec-test-001"
    assert context.agent_id == "test-agent"
    assert context.deadline is None
    assert context.trace_id == "trace-test-001"


def test_cancellation_token_structural_typing() -> None:
    token: CancellationToken = FakeCancellationToken()

    assert token.cancelled is False


def test_cancellation_token_waits_until_cancelled() -> None:
    async def scenario() -> None:
        token = FakeCancellationToken()

        waiter = asyncio.create_task(token.wait())

        await asyncio.sleep(0)
        assert not waiter.done()

        token.cancel()
        await waiter

        assert token.cancelled

    asyncio.run(scenario())
