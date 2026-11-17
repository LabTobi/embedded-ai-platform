"""Runtime metadata describing an executable agent."""

from dataclasses import dataclass
from typing import Generic, TypeVar

from pydantic import BaseModel

from embedded_ai_platform.contracts.agent import Agent

InputT = TypeVar("InputT", bound=BaseModel)
OutputT = TypeVar("OutputT", bound=BaseModel)


@dataclass(frozen=True, slots=True)
class AgentDescriptor(Generic[InputT, OutputT]):
    """Metadata required by the runtime to execute an agent."""

    agent_id: str
    agent: Agent[InputT, OutputT]
    input_model: type[InputT]
    output_model: type[OutputT]

    def __post_init__(self) -> None:
        """Validate descriptor metadata."""

        if not isinstance(self.agent_id, str) or not self.agent_id.strip():
            raise ValueError("agent_id must be a non-empty string.")

        if not isinstance(self.input_model, type) or not issubclass(self.input_model, BaseModel):
            raise TypeError("input_model must be a Pydantic BaseModel subclass.")

        if not isinstance(self.output_model, type) or not issubclass(self.output_model, BaseModel):
            raise TypeError("output_model must be a Pydantic BaseModel subclass.")
