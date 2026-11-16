"""Unit tests for the Agent protocol."""

import asyncio
from logging import Logger, getLogger

from pydantic import BaseModel

from embedded_ai_platform.contracts import (
    Agent,
    CancellationToken,
    ExecutionContext,
)


class BootLogInput(BaseModel):
    """Input for boot log analysis."""

    log_content: str


class BootLogOutput(BaseModel):
    """Output from boot log analysis."""

    kernel_version: str
    has_panic: bool


class FakeCancellationToken:
    """Minimal cancellation token for testing."""

    @property
    def cancelled(self) -> bool:
        return False

    async def wait(self) -> None:
        await asyncio.Event().wait()


class FakeExecutionContext:
    """Minimal execution context for testing."""

    @property
    def execution_id(self) -> str:
        return "exec-agent-001"

    @property
    def agent_id(self) -> str:
        return "boot-log-analyzer"

    @property
    def cancellation_token(self) -> CancellationToken:
        return FakeCancellationToken()

    @property
    def deadline(self) -> float | None:
        return None

    @property
    def logger(self) -> Logger:
        return getLogger("tests.agent")

    @property
    def trace_id(self) -> str | None:
        return None


class BootLogAnalyzer:
    """Example agent without inheriting from the Agent protocol."""

    async def run(
        self,
        input_data: BootLogInput,
        context: ExecutionContext,
    ) -> BootLogOutput:
        context.logger.info("Analyzing boot log: %s", context.execution_id)

        return BootLogOutput(
            kernel_version="6.1.0",
            has_panic="Kernel panic" in input_data.log_content,
        )


def test_agent_structural_typing() -> None:
    agent: Agent[BootLogInput, BootLogOutput] = BootLogAnalyzer()

    assert agent is not None


def test_agent_run_returns_structured_output() -> None:
    async def scenario() -> None:
        agent: Agent[BootLogInput, BootLogOutput] = BootLogAnalyzer()

        result = await agent.run(
            BootLogInput(log_content="Kernel panic - not syncing"),
            FakeExecutionContext(),
        )

        assert isinstance(result, BootLogOutput)
        assert result.kernel_version == "6.1.0"
        assert result.has_panic is True

    asyncio.run(scenario())


def test_agent_run_handles_normal_boot_log() -> None:
    async def scenario() -> None:
        agent: Agent[BootLogInput, BootLogOutput] = BootLogAnalyzer()

        result = await agent.run(
            BootLogInput(log_content="Linux version 6.1.0"),
            FakeExecutionContext(),
        )

        assert result.has_panic is False

    asyncio.run(scenario())
