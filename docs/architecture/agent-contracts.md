# Agent Contracts

## Agent protocol

`Agent[InputT, OutputT]` is an async-first structural protocol. Its single operation accepts
an input model and `ExecutionContext`, and returns an output model:

```python
async def run(input_data: InputT, context: ExecutionContext) -> OutputT: ...
```

Both generic model types are bounded by Pydantic `BaseModel`. Input is contravariant and
output is covariant so normal substitutability rules are represented in static typing.
Implementations do not inherit from `Agent`; a matching method is sufficient.

Agents are responsible for domain behavior and structured output. They should cooperate
with cancellation, respect the supplied deadline, use the execution logger, and avoid
embedding runtime lifecycle policy.

## Agent descriptor

`AgentDescriptor[InputT, OutputT]` connects an agent implementation to its runtime metadata.
It is a frozen, slotted dataclass with:

- `agent_id`: a non-empty string (whitespace-only strings are rejected).
- `agent`: the structurally typed implementation.
- `input_model`: a Pydantic model class.
- `output_model`: a Pydantic model class.

The descriptor validates model classes at construction and is immutable afterward. The
future runtime should use these declared classes for boundary validation and output checks.
The descriptor must not accumulate execution state.

## Execution context

`ExecutionContext` is a read-only protocol scoped to one execution. It exposes:

- `execution_id` and `agent_id` for identity.
- `cancellation_token` for cooperative cancellation.
- `deadline`, an optional absolute monotonic deadline.
- `logger`, scoped for execution diagnostics.
- optional `trace_id` for correlation.

The runtime owns the concrete context and cancellation implementation. Context instances
must not be reused as global mutable state or across unrelated executions.

## Errors and results

`ErrorInfo` is immutable, rejects extra fields, and carries a category, stable code,
human-readable message, retry hint, and JSON-compatible details. Producers must sanitize
details and exclude secrets.

`ExecutionResult[OutputT]` is immutable and rejects extra fields. Its state machine is:

| Status | Required | Forbidden or constrained |
| --- | --- | --- |
| `PENDING` | IDs only | No output, error, or timestamps |
| `RUNNING` | `started_at` | No output, error, or `completed_at` |
| `SUCCEEDED` | Output and both timestamps | No error |
| `FAILED` | Error and both timestamps | No output |
| `CANCELLED` | `completed_at` | No output; may occur before start |
| `TIMED_OUT` | Both timestamps | No output |

All present timestamps must be timezone-aware, and completion cannot precede start. These
rules are part of the public Core Contracts and must not be weakened by runtime code.

## Compatibility rules

Changes to public fields, enum values, generic variance, validation, serialization, or
state combinations are contract changes. They require explicit architecture review and
corresponding tests. Runtime implementation work must adapt to these contracts rather than
silently changing them.
