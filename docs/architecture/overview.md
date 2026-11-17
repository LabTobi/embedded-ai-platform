# Architecture Overview

## Purpose

Embedded AI Platform is a reusable foundation for structured AI agents used in Embedded
Linux engineering workflows. The current repository defines the contracts an agent and a
future runtime share; it does not yet contain a Runtime Engine.

## Current components

The package currently has two architectural areas:

- `embedded_ai_platform.contracts` contains the public agent, context, error, and execution
  contracts.
- `embedded_ai_platform.runtime` currently contains only `AgentDescriptor`, the metadata
  boundary through which a future runtime will receive an executable agent.

Tests exercise structural protocol conformance, descriptor validation and immutability,
cooperative cancellation semantics, and the execution-result state machine.

## Component boundaries

An agent accepts a Pydantic input model and an execution-scoped `ExecutionContext`, then
asynchronously returns a Pydantic output model. The agent is structurally typed and does not
need to inherit from a framework base class.

`AgentDescriptor` binds four values:

1. A non-empty agent ID.
2. An implementation satisfying the async `Agent` protocol.
3. A Pydantic input model class.
4. A Pydantic output model class.

The future runtime will consume the descriptor, own the execution lifecycle, and produce an
`ExecutionResult`. It will validate data at model boundaries without taking ownership of
agent domain logic.

## Dependency direction

Contracts are the stable center of the design. Agent implementations and runtime machinery
may depend on contracts. Contracts must not depend on concrete agents, a runtime
implementation, an LLM SDK, or an external service.

Provider integrations, when required, should live outside the core runtime and satisfy
narrow provider-neutral interfaces justified by concrete use cases. The core execution
lifecycle must remain usable for agents that do not call an LLM.

## Time and cancellation

Lifecycle timestamps in `ExecutionResult` are timezone-aware wall-clock datetimes suitable
for records and observability. `ExecutionContext.deadline` is instead an absolute monotonic
clock value suitable for timeout calculations. These two time domains must not be mixed.

Cancellation is cooperative. Agents inspect or await the execution-scoped
`CancellationToken`; the runtime coordinates the request and maps the final lifecycle state.

## Design status

The Core Contracts and `AgentDescriptor` are implemented and tested. Runtime lifecycle
details in this documentation are constraints for the next design phase, not an implemented
engine or a commitment to additional abstractions.
