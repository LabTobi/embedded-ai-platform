"""Tests for the AgentDescriptor runtime contract."""

from dataclasses import FrozenInstanceError, dataclass
from typing import cast

import pytest
from pydantic import BaseModel

from embedded_ai_platform.contracts.context import ExecutionContext
from embedded_ai_platform.runtime.descriptor import AgentDescriptor


class BootLogInput(BaseModel):
    """Input model for boot log analysis."""

    log_content: str


class BootLogOutput(BaseModel):
    """Output model for boot log analysis."""

    summary: str


@dataclass
class BootLogAnalyzer:
    """Example agent using structural typing."""

    async def run(
        self,
        input_data: BootLogInput,
        context: ExecutionContext,
    ) -> BootLogOutput:
        """Analyze boot logs."""

        return BootLogOutput(summary=input_data.log_content)


def test_create_valid_agent_descriptor() -> None:
    agent = BootLogAnalyzer()

    descriptor = AgentDescriptor(
        agent_id="boot-log-analyzer",
        agent=agent,
        input_model=BootLogInput,
        output_model=BootLogOutput,
    )

    assert descriptor.agent_id == "boot-log-analyzer"
    assert descriptor.agent is agent
    assert descriptor.input_model is BootLogInput
    assert descriptor.output_model is BootLogOutput


@pytest.mark.parametrize("agent_id", ["", " ", "   ", "\t"])
def test_reject_invalid_agent_id(agent_id: str) -> None:
    with pytest.raises(ValueError, match="agent_id"):
        AgentDescriptor(
            agent_id=agent_id,
            agent=BootLogAnalyzer(),
            input_model=BootLogInput,
            output_model=BootLogOutput,
        )


def test_reject_invalid_input_model() -> None:
    invalid_model = cast(type[BootLogInput], str)

    with pytest.raises(TypeError, match="input_model"):
        AgentDescriptor(
            agent_id="boot-log-analyzer",
            agent=BootLogAnalyzer(),
            input_model=invalid_model,
            output_model=BootLogOutput,
        )


def test_reject_invalid_output_model() -> None:
    invalid_model = cast(type[BootLogOutput], dict)

    with pytest.raises(TypeError, match="output_model"):
        AgentDescriptor(
            agent_id="boot-log-analyzer",
            agent=BootLogAnalyzer(),
            input_model=BootLogInput,
            output_model=invalid_model,
        )


def test_descriptor_is_frozen() -> None:
    descriptor = AgentDescriptor(
        agent_id="boot-log-analyzer",
        agent=BootLogAnalyzer(),
        input_model=BootLogInput,
        output_model=BootLogOutput,
    )

    with pytest.raises(FrozenInstanceError):
        descriptor.agent_id = "another-agent"  # type: ignore[misc]


def test_agent_uses_structural_typing() -> None:
    agent = BootLogAnalyzer()

    descriptor = AgentDescriptor(
        agent_id="boot-log-analyzer",
        agent=agent,
        input_model=BootLogInput,
        output_model=BootLogOutput,
    )

    assert descriptor.agent is agent
