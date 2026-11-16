"""Agent interface contracts."""

from typing import Protocol, TypeVar

from pydantic import BaseModel

from embedded_ai_platform.contracts.context import ExecutionContext

InputT = TypeVar("InputT", bound=BaseModel, contravariant=True)
OutputT = TypeVar("OutputT", bound=BaseModel, covariant=True)


class Agent(Protocol[InputT, OutputT]):
    """Interface implemented by all platform agents."""

    async def run(
        self,
        input_data: InputT,
        context: ExecutionContext,
    ) -> OutputT:
        """Execute the agent task and return a structured result."""
        ...
