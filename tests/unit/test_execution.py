"""Unit tests for execution contracts."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import BaseModel, ValidationError

from embedded_ai_platform.contracts import (
    ErrorCategory,
    ErrorInfo,
    ExecutionResult,
    ExecutionStatus,
)


class BootAnalysis(BaseModel):
    kernel_version: str
    has_panic: bool


def make_error() -> ErrorInfo:
    return ErrorInfo(
        category=ErrorCategory.AGENT,
        code="ANALYSIS_FAILED",
        message="Boot log analysis failed.",
    )


def test_pending_execution_is_valid() -> None:
    result = ExecutionResult[BootAnalysis](
        execution_id="exec-001",
        agent_id="boot-log-analyzer",
        status=ExecutionStatus.PENDING,
    )

    assert result.status == ExecutionStatus.PENDING
    assert result.output is None
    assert result.error is None


def test_running_execution_requires_started_at() -> None:
    result = ExecutionResult[BootAnalysis](
        execution_id="exec-002",
        agent_id="boot-log-analyzer",
        status=ExecutionStatus.RUNNING,
        started_at=datetime.now(UTC),
    )

    assert result.status == ExecutionStatus.RUNNING


def test_succeeded_execution_requires_output_and_timestamps() -> None:
    now = datetime.now(UTC)

    result = ExecutionResult[BootAnalysis](
        execution_id="exec-003",
        agent_id="boot-log-analyzer",
        status=ExecutionStatus.SUCCEEDED,
        output=BootAnalysis(kernel_version="6.1.0", has_panic=True),
        started_at=now,
        completed_at=now + timedelta(seconds=2),
    )

    assert result.output is not None
    assert result.output.has_panic is True


def test_failed_execution_with_error_is_valid() -> None:
    now = datetime.now(UTC)

    result = ExecutionResult[BootAnalysis](
        execution_id="exec-004",
        agent_id="boot-log-analyzer",
        status=ExecutionStatus.FAILED,
        error=make_error(),
        started_at=now,
        completed_at=now + timedelta(seconds=1),
    )

    assert result.error is not None
    assert result.error.code == "ANALYSIS_FAILED"


def test_cancelled_execution_can_be_cancelled_before_start() -> None:
    result = ExecutionResult[BootAnalysis](
        execution_id="exec-005",
        agent_id="boot-log-analyzer",
        status=ExecutionStatus.CANCELLED,
        completed_at=datetime.now(UTC),
    )

    assert result.status == ExecutionStatus.CANCELLED
    assert result.started_at is None


def test_timed_out_execution_requires_started_at() -> None:
    now = datetime.now(UTC)

    result = ExecutionResult[BootAnalysis](
        execution_id="exec-006",
        agent_id="boot-log-analyzer",
        status=ExecutionStatus.TIMED_OUT,
        started_at=now,
        completed_at=now + timedelta(seconds=30),
    )

    assert result.status == ExecutionStatus.TIMED_OUT


def test_succeeded_execution_requires_output() -> None:
    now = datetime.now(UTC)

    with pytest.raises(ValidationError):
        ExecutionResult[BootAnalysis](
            execution_id="exec-007",
            agent_id="boot-log-analyzer",
            status=ExecutionStatus.SUCCEEDED,
            started_at=now,
            completed_at=now + timedelta(seconds=1),
        )


def test_failed_execution_requires_error() -> None:
    now = datetime.now(UTC)

    with pytest.raises(ValidationError):
        ExecutionResult[BootAnalysis](
            execution_id="exec-008",
            agent_id="boot-log-analyzer",
            status=ExecutionStatus.FAILED,
            started_at=now,
            completed_at=now + timedelta(seconds=1),
        )


def test_running_execution_cannot_have_completed_at() -> None:
    now = datetime.now(UTC)

    with pytest.raises(ValidationError):
        ExecutionResult[BootAnalysis](
            execution_id="exec-009",
            agent_id="boot-log-analyzer",
            status=ExecutionStatus.RUNNING,
            started_at=now,
            completed_at=now + timedelta(seconds=1),
        )


def test_execution_timestamps_must_be_timezone_aware() -> None:
    with pytest.raises(ValidationError):
        ExecutionResult[BootAnalysis](
            execution_id="exec-010",
            agent_id="boot-log-analyzer",
            status=ExecutionStatus.RUNNING,
            started_at=datetime.now(),
        )


def test_completed_at_cannot_precede_started_at() -> None:
    now = datetime.now(UTC)

    with pytest.raises(ValidationError):
        ExecutionResult[BootAnalysis](
            execution_id="exec-011",
            agent_id="boot-log-analyzer",
            status=ExecutionStatus.SUCCEEDED,
            output=BootAnalysis(kernel_version="6.1.0", has_panic=False),
            started_at=now,
            completed_at=now - timedelta(seconds=1),
        )


def test_execution_result_json_round_trip() -> None:
    now = datetime.now(UTC)

    original = ExecutionResult[BootAnalysis](
        execution_id="exec-012",
        agent_id="boot-log-analyzer",
        status=ExecutionStatus.SUCCEEDED,
        output=BootAnalysis(kernel_version="6.1.0", has_panic=False),
        started_at=now,
        completed_at=now + timedelta(seconds=2),
    )

    restored = ExecutionResult[BootAnalysis].model_validate_json(original.model_dump_json())

    assert restored == original
    assert isinstance(restored.output, BootAnalysis)


def test_execution_id_cannot_be_empty() -> None:
    with pytest.raises(ValidationError):
        ExecutionResult[BootAnalysis](
            execution_id="",
            agent_id="test-agent",
            status=ExecutionStatus.PENDING,
        )


def test_agent_id_cannot_be_empty() -> None:
    with pytest.raises(ValidationError):
        ExecutionResult[BootAnalysis](
            execution_id="exec-001",
            agent_id="",
            status=ExecutionStatus.PENDING,
        )
