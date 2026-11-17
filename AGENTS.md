# Embedded AI Platform Development Guide

This file applies to the entire repository. Keep changes small, typed, tested, and aligned
with the architectural contracts below.

## Architecture rules

- Agents implement the async-first `Agent[InputT, OutputT]` protocol by structural typing.
- Agent inputs and outputs are Pydantic v2 `BaseModel` subclasses.
- `AgentDescriptor` is the runtime boundary for an agent ID, implementation, input model,
  and output model. Preserve its frozen value semantics and validation behavior.
- The runtime owns validation, execution lifecycle, timeouts, cancellation coordination,
  result construction, and execution-scoped resources. Agents own only domain behavior.
- `ExecutionContext` is created per execution and exposed to agents as a read-only protocol.
- Deadlines are absolute values from a monotonic clock. Do not compare them with wall-clock
  timestamps.
- Cancellation is cooperative through `CancellationToken`; runtime cancellation must not be
  represented as provider-specific behavior.
- Keep the runtime independent of LLM vendors, SDKs, transports, and model APIs. Provider
  integrations belong behind separate adapters when they are introduced.
- Preserve the `ExecutionResult` state-machine invariants. Do not weaken validation or add
  contradictory state combinations.
- Prefer the smallest concrete design that satisfies a current requirement. Do not add
  registries, dependency-injection frameworks, event buses, or provider abstractions before
  a demonstrated need.
- Do not implement the Runtime Engine until its architecture has been reviewed.

## Development conventions

- Support Python 3.11 and newer, and use `uv` for environments and commands.
- Use complete type annotations. The project runs mypy in strict mode.
- Use modern Python syntax and Pydantic v2 APIs.
- Keep public contracts under `embedded_ai_platform.contracts`; runtime-owned types belong
  under `embedded_ai_platform.runtime`.
- Treat public contract changes as compatibility-sensitive. Update tests and architecture
  documentation together with any approved contract change.
- Add focused unit tests for behavior and invalid states. Tests must be deterministic and
  must not require network access or external providers.
- Use timezone-aware datetimes for lifecycle records and monotonic time for deadlines.
- Keep error details structured, JSON-compatible, sanitized, and free of secrets.
- Follow Ruff formatting and the configured 100-character line length.
- Avoid unrelated refactors in feature changes.

## Validation

Run the complete validation suite before handing off a change:

```bash
uv run pytest -q
uv run mypy src/ tests/
uv run ruff check .
uv run ruff format --check .
uv build
git diff --check
```

Do not commit, push, or merge unless the user explicitly requests it.
