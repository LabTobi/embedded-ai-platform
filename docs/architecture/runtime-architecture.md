# Runtime Architecture

## Status and scope

This document records the approved IMP-02.1 architecture for the future Runtime Engine.
The decisions below are implementation constraints, not deferred design proposals. The
engine is intentionally not implemented in this documentation task, and the existing public
contracts remain unchanged.

The runtime is async-first and provider-independent. Its execution API awaits one agent
execution and returns a structured `ExecutionResult`. The exact public function and method
names may be selected during implementation without changing the decisions in this document.

## Execution boundary and ownership

`AgentDescriptor` is the execution boundary. It supplies the agent ID, async agent
implementation, input model, and output model needed for an execution.

An `ExecutionRunner` owns exactly one execution lifecycle. It owns that execution's state,
context, cancellation signal, deadline, timestamps, exception mapping, and final result. It
must not retain mutable state shared with another execution. Concurrent requests therefore
use independent runners and independent execution-scoped state, even when they use the same
descriptor or agent implementation.

The runtime owns lifecycle policy and boundary validation. It does not own agent business
logic, prompts, model selection, provider clients, or embedded-domain policy.

## Execution lifecycle

The required flow is:

```text
PENDING -> RUNNING -> Input Validation -> Agent Execution
                   -> Output Validation -> Terminal Result
```

The runner establishes the execution identity and initial `PENDING` state, then transitions
to `RUNNING` before validating input. Entering `RUNNING` records a timezone-aware
`started_at`. This ordering ensures every validation attempt is part of an observable
execution lifecycle.

Input is validated against the descriptor's input model. Invalid input terminates the
running execution as `FAILED` with `ErrorInfo.category` set to `ErrorCategory.INPUT`; the
agent is not invoked. Successful input validation is followed by asynchronous agent
execution. The returned value is then validated at the descriptor's output-model boundary
before success is recorded.

Each execution reaches exactly one terminal result: `SUCCEEDED`, `FAILED`, `CANCELLED`, or
`TIMED_OUT`. Competing completion, failure, cancellation, and timeout signals must be
resolved by the runner so that no later event can replace the selected terminal result.

All results must preserve the existing `ExecutionResult` state invariants:

- `PENDING` has no output, error, or timestamps.
- `RUNNING` has `started_at` and no output, error, or `completed_at`.
- `SUCCEEDED` has output and both timestamps, and no error.
- `FAILED` has an error and both timestamps, and no output.
- `CANCELLED` has `completed_at`, no output, and may omit `started_at` when cancellation wins
  before execution starts.
- `TIMED_OUT` has both timestamps and no output.
- All timestamps are timezone-aware, and completion cannot precede start.

## Timeout and deadline handling

The runtime provides a default timeout. Each execution may override that default through
the async runtime API. The effective timeout is resolved for the execution and converted
once into an absolute monotonic deadline. Remaining time is calculated as
`deadline - monotonic_now`; wall-clock datetimes are used only for lifecycle records.

A timed-out execution must return `TIMED_OUT` with an `ErrorInfo` whose category is
`ErrorCategory.RUNTIME` and whose code is `EXECUTION_TIMEOUT`. Requiring that timeout error
is an approved IMP-02.1 requirement, but it is not yet enforced by the existing
`ExecutionResult` model. Runtime implementation must supply it; changing public contract
validation requires separate, explicitly scoped work.

Clock access should be localized enough for deterministic tests without introducing a broad
timing framework.

## Cooperative cancellation and cleanup

The runtime owns the mutable cancellation signal and exposes only the read-only
`CancellationToken` through the execution-scoped context. A cancellation request sets the
signal; agents cooperate by checking `cancelled` or awaiting `wait()` at safe points.

Cancellation cleanup is bounded. After cancellation or timeout wins, the runner allows only
a finite cleanup interval for cooperative agent cleanup; it must not wait indefinitely.
Cleanup completion, cleanup failure, or expiry of the cleanup bound cannot replace the
already selected terminal result. Provider-specific cancellation behavior must not leak
into runtime contracts.

## Structured errors and exception mapping

The runtime uses a structured `PlatformError` hierarchy internally. Platform errors carry
stable classification data that can be converted into sanitized public `ErrorInfo` without
exposing traceback data, secrets, provider payloads, or arbitrary exception text.

Exception mapping is boundary-aware:

- Input-boundary validation failures map to `FAILED` with `ErrorCategory.INPUT`.
- Exceptions raised during agent execution map at the agent boundary using the structured
  platform error when present; unexpected agent exceptions are sanitized and classified as
  agent failures.
- Output-boundary validation failures are runtime boundary failures, not input failures.
- Runtime orchestration failures are classified as runtime errors.
- Timeout maps to `TIMED_OUT` with category `RUNTIME` and code `EXECUTION_TIMEOUT`.
- Cooperative cancellation maps to `CANCELLED`, subject to the exactly-one-terminal-result
  rule.

Detailed subclass names and the complete mapping table belong to the Runtime Engine
implementation design, but they must preserve these boundary classifications and the public
`ErrorInfo` contract.

## Provider independence

The Runtime Engine invokes agents, not LLM providers. Agents may use provider integrations,
but the runtime lifecycle cannot import vendor SDKs or encode provider concepts such as
models, tokens, chats, or tool-call formats.

Provider exceptions must not cross the runtime boundary unexamined. The owning integration
maps them into the structured error model, and the runner emits only sanitized `ErrorInfo`.
Provider adapter abstractions should be introduced only when concrete integrations
demonstrate a shared boundary.

## Out of scope

The first Runtime Engine does not include registries, persistence, retries, queues,
dependency-injection containers, event buses, distributed execution, or provider-specific
APIs. Observability extensions beyond the existing execution logger and trace identifier
require separate justification.
