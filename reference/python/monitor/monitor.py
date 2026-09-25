"""AARC v1.1.0 executable reference monitor.

The monitor provides hash-chained runtime events, immutable role/objective/policy
anchors, fail-closed tool authorization, separated Actor/Critic/Judge approval
receipts, and deterministic trace verification. It deliberately does not record
hidden chain-of-thought.
"""

from __future__ import annotations

import copy
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, TextIO


ZERO_HASH = "0" * 64
SCHEMA_VERSION = "1.1.0"
TERMINAL_EVENTS = {"task.stop", "task.fail"}


class TraceVerificationError(ValueError):
    """Raised when a committed trace violates the AARC runtime contract."""


class ToolAuthorizationError(PermissionError):
    """Raised after a denied tool request has been committed to the trace."""


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_hex(value: Any) -> str:
    if not isinstance(value, str):
        value = canonical_json(value)
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def compute_event_hash(event: Mapping[str, Any]) -> str:
    material = dict(event)
    material.pop("event_hash", None)
    return sha256_hex(material)


@dataclass(frozen=True)
class ToolPermit:
    tool_name: str
    request_event_id: str
    permit_event_id: str


class Monitor:
    """Authoritative AARC event committer for one task run."""

    def __init__(
        self,
        *,
        agent_id: str,
        task_id: str,
        objective: str,
        policy: Mapping[str, Any],
        role: str = "actor",
        root_agent_id: Optional[str] = None,
        parent_agent_id: Optional[str] = None,
        run_id: Optional[str] = None,
        allowed_tools: Iterable[str] = (),
        stream: Optional[TextIO] = None,
    ) -> None:
        if not agent_id or not task_id or not objective or not role:
            raise ValueError("agent_id, task_id, objective, and role are required")
        self.agent_id = agent_id
        self.root_agent_id = root_agent_id or agent_id
        self.parent_agent_id = parent_agent_id
        self.task_id = task_id
        self.run_id = run_id or str(uuid.uuid4())
        self.role = role
        self.objective = objective
        self.policy = copy.deepcopy(dict(policy))
        self.allowed_tools = frozenset(allowed_tools)
        self.stream = stream
        self.sequence = 0
        self.events: List[Dict[str, Any]] = []
        self.anchors = {
            "role_hash": sha256_hex(role),
            "objective_hash": sha256_hex(objective),
            "policy_hash": sha256_hex(self.policy),
        }

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _emit(
        self,
        event_type: str,
        payload: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        if self.events and self.events[-1]["event_type"] in TERMINAL_EVENTS:
            raise RuntimeError("cannot emit after a terminal event")
        self.sequence += 1
        event: Dict[str, Any] = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": self._timestamp(),
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "run_id": self.run_id,
            "sequence": self.sequence,
            "anchors": dict(self.anchors),
            "prev_event_hash": self.events[-1]["event_hash"] if self.events else ZERO_HASH,
            "payload": copy.deepcopy(dict(payload or {})),
        }
        event["event_hash"] = compute_event_hash(event)
        self.events.append(event)
        if self.stream is not None:
            self.stream.write(canonical_json(event) + "\n")
            self.stream.flush()
        return copy.deepcopy(event)

    def task_start(
        self,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        if self.events:
            raise RuntimeError("task.start must be the first event")
        payload = {
            "schema_version": SCHEMA_VERSION,
            "root_agent_id": self.root_agent_id,
            "parent_agent_id": self.parent_agent_id,
            "role": self.role,
            "objective_digest": self.anchors["objective_hash"],
            "policy_digest": self.anchors["policy_hash"],
        }
        payload.update(dict(metadata or {}))
        return self._emit("task.start", payload)

    def heartbeat(self, note: Optional[str] = None) -> Dict[str, Any]:
        return self._emit("task.heartbeat", {"note": note} if note else {})

    def snapshot_state(
        self,
        *,
        inputs: Mapping[str, Any],
        outputs: Mapping[str, Any],
        tools: Sequence[Mapping[str, Any]] = (),
        confidence: Optional[Mapping[str, Any]] = None,
        assumptions: Sequence[str] = (),
        evidence_refs: Sequence[str] = (),
    ) -> Dict[str, Any]:
        next_sequence = self.sequence + 1
        state = {
            "schema_version": SCHEMA_VERSION,
            "identity": {
                "agent_id": self.agent_id,
                "root_agent_id": self.root_agent_id,
                "parent_agent_id": self.parent_agent_id,
                "role": self.role,
                "role_hash": self.anchors["role_hash"],
            },
            "intent": {
                "objective_hash": self.anchors["objective_hash"],
                "policy_hash": self.anchors["policy_hash"],
            },
            "trace": {
                "run_id": self.run_id,
                "task_id": self.task_id,
                "step_id": f"step-{next_sequence}",
                "sequence": next_sequence,
                "parent_event_hash": (
                    self.events[-1]["event_hash"] if self.events else ZERO_HASH
                ),
            },
            "inputs": copy.deepcopy(dict(inputs)),
            "outputs": copy.deepcopy(dict(outputs)),
            "tools": [copy.deepcopy(dict(item)) for item in tools],
            "confidence": copy.deepcopy(dict(confidence or {})),
            "policy": copy.deepcopy(self.policy),
            "assumptions": list(assumptions),
            "evidence_refs": list(evidence_refs),
        }
        return self._emit("state.snapshot", state)

    def request_tool(
        self,
        tool_name: str,
        arguments: Mapping[str, Any],
    ) -> ToolPermit:
        args_digest = sha256_hex(dict(arguments))
        request = self._emit(
            "tool.requested",
            {"tool_name": tool_name, "arguments_digest": args_digest},
        )
        decision_payload = {
            "tool_name": tool_name,
            "request_event_id": request["event_id"],
            "arguments_digest": args_digest,
            "policy_hash": self.anchors["policy_hash"],
        }
        if tool_name not in self.allowed_tools:
            self._emit("tool.denied", decision_payload)
            raise ToolAuthorizationError(f"tool denied by policy: {tool_name}")
        authorized = self._emit("tool.authorized", decision_payload)
        return ToolPermit(
            tool_name=tool_name,
            request_event_id=request["event_id"],
            permit_event_id=authorized["event_id"],
        )

    def record_tool_result(
        self,
        permit: ToolPermit,
        result: Any,
        *,
        failed: bool = False,
    ) -> Dict[str, Any]:
        payload = {
            "tool_name": permit.tool_name,
            "request_event_id": permit.request_event_id,
            "permit_event_id": permit.permit_event_id,
            "result_digest": sha256_hex(result),
        }
        return self._emit("tool.failed" if failed else "tool.executed", payload)

    def record_approval_decision(
        self,
        *,
        actor_id: str,
        critic_id: str,
        judge_id: str,
        proposal: Any,
        critique: Any,
        decision: str,
        evidence_refs: Sequence[str],
    ) -> Dict[str, Any]:
        if decision not in {"approved", "rejected"}:
            raise ValueError("decision must be approved or rejected")
        if decision == "approved":
            identities = {actor_id, critic_id, judge_id}
            if len(identities) != 3:
                raise ValueError(
                    "positive approval requires pairwise-distinct Actor/Critic/Judge"
                )
            if not evidence_refs:
                raise ValueError("positive approval requires evidence_refs")
        return self._emit(
            "approval.decided",
            {
                "actor_id": actor_id,
                "critic_id": critic_id,
                "judge_id": judge_id,
                "proposal_hash": sha256_hex(proposal),
                "critique_hash": sha256_hex(critique),
                "decision": decision,
                "evidence_refs": list(evidence_refs),
            },
        )

    def remediate(
        self,
        remediation_id: str,
        strategy: str,
        outcome: str,
    ) -> Dict[str, Any]:
        return self._emit(
            "task.remediate",
            {
                "remediation_id": remediation_id,
                "strategy": strategy,
                "outcome": outcome,
            },
        )

    def task_fail(
        self,
        failure_class: str,
        failure_summary: str,
        impact: str,
    ) -> Dict[str, Any]:
        return self._emit(
            "task.fail",
            {
                "failure_class": failure_class,
                "failure_summary": failure_summary,
                "impact": impact,
            },
        )

    def task_stop(self, summary: Optional[str] = None) -> Dict[str, Any]:
        return self._emit("task.stop", {"summary": summary} if summary else {})


def verify_trace(
    events: Sequence[Mapping[str, Any]],
    *,
    allowed_tools: Optional[Iterable[str]] = None,
    require_terminal: bool = True,
) -> None:
    """Verify AARC v1.1.0 structural and semantic invariants."""
    if not events:
        raise TraceVerificationError("empty trace")
    if events[0].get("event_type") != "task.start":
        raise TraceVerificationError("trace must begin with task.start")

    expected_anchors = events[0].get("anchors")
    if not isinstance(expected_anchors, Mapping):
        raise TraceVerificationError("missing genesis anchors")

    permits: Dict[str, Dict[str, Any]] = {}
    denied_requests = set()
    terminal_seen = False
    allowed = frozenset(allowed_tools) if allowed_tools is not None else None
    previous_hash = ZERO_HASH

    for index, raw in enumerate(events, start=1):
        event = dict(raw)
        if terminal_seen:
            raise TraceVerificationError("event appears after terminal event")
        if event.get("sequence") != index:
            raise TraceVerificationError("non-contiguous event sequence")
        if event.get("prev_event_hash") != previous_hash:
            raise TraceVerificationError("broken previous-event hash link")
        if event.get("event_hash") != compute_event_hash(event):
            raise TraceVerificationError("event hash mismatch")
        if event.get("anchors") != expected_anchors:
            raise TraceVerificationError("immutable anchor drift")

        event_type = event.get("event_type")
        payload = event.get("payload")
        if not isinstance(payload, Mapping):
            raise TraceVerificationError("payload must be an object")

        if event_type == "tool.denied":
            request_id = payload.get("request_event_id")
            if request_id:
                denied_requests.add(request_id)

        elif event_type == "tool.authorized":
            request_id = payload.get("request_event_id")
            tool_name = payload.get("tool_name")
            if not request_id or not tool_name:
                raise TraceVerificationError("malformed tool authorization")
            if request_id in denied_requests:
                raise TraceVerificationError("request both denied and authorized")
            if allowed is not None and tool_name not in allowed:
                raise TraceVerificationError("authorization violates verifier policy")
            permits[event["event_id"]] = {
                "request_event_id": request_id,
                "tool_name": tool_name,
            }

        elif event_type in {"tool.executed", "tool.failed"}:
            permit_id = payload.get("permit_event_id")
            request_id = payload.get("request_event_id")
            tool_name = payload.get("tool_name")
            permit = permits.get(permit_id)
            if permit is None:
                raise TraceVerificationError("tool execution without valid permit")
            if (
                permit["request_event_id"] != request_id
                or permit["tool_name"] != tool_name
            ):
                raise TraceVerificationError("tool execution does not match permit")
            if request_id in denied_requests:
                raise TraceVerificationError("denied tool request was executed")
            if allowed is not None and tool_name not in allowed:
                raise TraceVerificationError("executed tool violates verifier policy")

        elif event_type == "approval.decided" and payload.get("decision") == "approved":
            identities = {
                payload.get("actor_id"),
                payload.get("critic_id"),
                payload.get("judge_id"),
            }
            if None in identities or len(identities) != 3:
                raise TraceVerificationError(
                    "self-approval or missing SDV identity"
                )
            if not payload.get("proposal_hash") or not payload.get("critique_hash"):
                raise TraceVerificationError(
                    "approval missing proposal/critique digest"
                )
            if not payload.get("evidence_refs"):
                raise TraceVerificationError("approval missing evidence")

        if event_type in TERMINAL_EVENTS:
            terminal_seen = True

        previous_hash = event["event_hash"]

    if require_terminal and events[-1].get("event_type") not in TERMINAL_EVENTS:
        raise TraceVerificationError("trace is not terminal")


def rehash_trace(
    events: Sequence[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    """Recompute a chain after intentional mutation in adversarial fixtures."""
    output: List[Dict[str, Any]] = []
    previous_hash = ZERO_HASH
    for raw in events:
        event = copy.deepcopy(dict(raw))
        event["prev_event_hash"] = previous_hash
        event["event_hash"] = compute_event_hash(event)
        output.append(event)
        previous_hash = event["event_hash"]
    return output


def main() -> None:
    monitor = Monitor(
        agent_id="agent-demo",
        task_id="task-demo",
        objective="demonstrate AARC",
        policy={"policy_id": "demo", "constraints": ["read-only"]},
        allowed_tools={"lookup"},
        stream=sys.stdout,
    )
    monitor.task_start()
    monitor.snapshot_state(inputs={"query": "health check"}, outputs={})
    permit = monitor.request_tool("lookup", {"key": "status"})
    monitor.record_tool_result(permit, {"status": "ok"})
    monitor.task_stop("completed")
    verify_trace(monitor.events, allowed_tools={"lookup"})


if __name__ == "__main__":
    main()
