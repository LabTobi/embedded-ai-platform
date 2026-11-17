# Roadmap

The roadmap is deliberately incremental. Each phase should preserve the Core Contracts,
remain provider-neutral, and add abstractions only when required by tested behavior.

## Phase 0: Foundation and bootstrap

- Define the async `Agent` protocol and Pydantic input/output boundaries.
- Define execution context, cancellation, error, and result contracts.
- Define and test the immutable `AgentDescriptor`.
- Document architectural boundaries and development conventions.
- Establish CI for tests, strict typing, linting, formatting, packaging, and diff hygiene.

Status: implemented by the repository foundation and this bootstrap task.

## Phase 1: Runtime architecture review

- Review lifecycle transitions and the public execution API.
- Specify input/output validation ownership.
- Define monotonic timeout and cooperative cancellation race semantics.
- Define exception-to-`ErrorInfo` classification and sanitization rules.
- Agree on deterministic testing seams for clock and execution coordination.

Exit criterion: an approved, minimal runtime design. No Runtime Engine should be implemented
before this review.

## Phase 2: Minimal Runtime Engine

- Implement one asynchronous in-process execution path.
- Create execution-scoped context and cancellation implementations.
- Enforce monotonic deadlines and the existing result state machine.
- Add deterministic unit tests for success, validation failure, agent failure, cancellation,
  timeout, and relevant races.

Provider clients, persistence, distributed execution, retries, and scheduling remain out of
scope.

## Phase 3: Integration boundary

- Build one representative Embedded Linux agent to validate the contracts end to end.
- Introduce provider adapters only if concrete agent integrations need them.
- Add integration tests that remain isolated from live external services by default.
- Revisit observability requirements using evidence from the first integration.

## Phase 4: Operational capabilities

Potential later work includes execution persistence, agent discovery, bounded concurrency,
retry policy, and external tooling. Each capability requires a separate design decision and
must not compromise provider independence or the execution state-machine contract.
