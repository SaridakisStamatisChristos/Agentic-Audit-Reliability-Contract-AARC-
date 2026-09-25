from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from evaluation.run_conformance_benchmark import (
    ALLOWED_TOOLS,
    MUTATIONS,
    healthy_trace,
)
from reference.python.monitor.monitor import (
    Monitor,
    ToolAuthorizationError,
    TraceVerificationError,
    canonical_json,
    sha256_hex,
    verify_trace,
)


ROOT = Path(__file__).resolve().parents[1]


def test_schemas_are_valid_json_schema() -> None:
    for name in (
        "AARC_STATE_VECTOR.schema.v1_1_0.json",
        "AARC_RUNTIME_EVENT.schema.v1_1_0.json",
    ):
        schema = json.loads(
            (ROOT / "spec" / name).read_text(encoding="utf-8")
        )
        Draft202012Validator.check_schema(schema)


def test_runtime_events_validate_against_schema() -> None:
    schema = json.loads(
        (
            ROOT
            / "spec"
            / "AARC_RUNTIME_EVENT.schema.v1_1_0.json"
        ).read_text(encoding="utf-8")
    )
    validator = Draft202012Validator(schema)
    for event in healthy_trace():
        validator.validate(event)


def test_state_snapshot_validates_against_schema() -> None:
    schema = json.loads(
        (
            ROOT
            / "spec"
            / "AARC_STATE_VECTOR.schema.v1_1_0.json"
        ).read_text(encoding="utf-8")
    )
    validator = Draft202012Validator(schema)
    snapshot = next(
        e
        for e in healthy_trace()
        if e["event_type"] == "state.snapshot"
    )
    validator.validate(snapshot["payload"])


def test_clean_trace_is_accepted() -> None:
    verify_trace(healthy_trace(), allowed_tools=ALLOWED_TOOLS)


@pytest.mark.parametrize("name", sorted(MUTATIONS))
def test_adversarial_trace_is_rejected(name: str) -> None:
    with pytest.raises(TraceVerificationError):
        verify_trace(
            MUTATIONS[name](healthy_trace()),
            allowed_tools=ALLOWED_TOOLS,
        )


def test_tool_gateway_fails_closed() -> None:
    monitor = Monitor(
        agent_id="agent",
        task_id="task",
        objective="read only",
        policy={"policy_id": "read-only"},
        allowed_tools={"lookup"},
    )
    monitor.task_start()
    with pytest.raises(ToolAuthorizationError):
        monitor.request_tool("delete", {"id": "x"})
    assert monitor.events[-1]["event_type"] == "tool.denied"


def test_positive_approval_rejects_self_approval() -> None:
    monitor = Monitor(
        agent_id="agent",
        task_id="task",
        objective="review",
        policy={"policy_id": "review"},
    )
    monitor.task_start()
    with pytest.raises(ValueError):
        monitor.record_approval_decision(
            actor_id="same",
            critic_id="critic",
            judge_id="same",
            proposal={"x": 1},
            critique={"x": 2},
            decision="approved",
            evidence_refs=["fixture://evidence"],
        )


def test_rfc8785_cross_language_vector() -> None:
    value = {"b": 1.0, "a": "x"}
    assert canonical_json(value) == '{"a":"x","b":1}'
    assert sha256_hex(value) == "cdab067e9f3beb32d1252cfd63e492592fecbf591b0d08cadb24bb17f3864246"
