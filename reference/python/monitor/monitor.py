"""Minimal ARF reference monitor for Python."""

from __future__ import annotations

import json
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class StateVector:
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    tools: List[Dict[str, Any]]
    confidence: Dict[str, Any]
    policy: Dict[str, Any]


@dataclass
class Monitor:
    agent_id: str
    task_id: str
    stream: Any = sys.stdout
    sequence: int = 0
    events: List[Dict[str, Any]] = field(default_factory=list)

    def _timestamp(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _next_sequence(self) -> int:
        self.sequence += 1
        return self.sequence

    def emit(self, event_type: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        event = {
            "event_id": str(uuid.uuid4()),
            "event_type": event_type,
            "timestamp": self._timestamp(),
            "agent_id": self.agent_id,
            "task_id": self.task_id,
            "sequence": self._next_sequence(),
            "payload": payload or {},
        }
        self.events.append(event)
        self.stream.write(json.dumps(event) + "\n")
        self.stream.flush()
        return event

    def task_start(self, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self.emit("task.start", metadata)

    def task_heartbeat(self, note: Optional[str] = None) -> Dict[str, Any]:
        payload = {"note": note} if note else {}
        return self.emit("task.heartbeat", payload)

    def task_stop(self, summary: Optional[str] = None) -> Dict[str, Any]:
        payload = {"summary": summary} if summary else {}
        return self.emit("task.stop", payload)

    def task_fail(self, failure_class: str, failure_summary: str, impact: str) -> Dict[str, Any]:
        payload = {
            "failure_class": failure_class,
            "failure_summary": failure_summary,
            "impact": impact,
        }
        return self.emit("task.fail", payload)

    def remediate(self, remediation_id: str, strategy: str, outcome: str) -> Dict[str, Any]:
        payload = {
            "remediation_id": remediation_id,
            "strategy": strategy,
            "outcome": outcome,
        }
        return self.emit("task.remediate", payload)

    def snapshot_state(self, state: StateVector) -> Dict[str, Any]:
        payload = {
            "inputs": state.inputs,
            "outputs": state.outputs,
            "tools": state.tools,
            "confidence": state.confidence,
            "policy": state.policy,
        }
        return self.emit("state.snapshot", payload)


def main() -> None:
    monitor = Monitor(agent_id="agent-demo", task_id="task-demo")
    monitor.task_start({"intent": "demo run"})
    monitor.snapshot_state(
        StateVector(
            inputs={"query": "health check"},
            outputs={},
            tools=[],
            confidence={"level": 0.74},
            policy={"constraints": ["no-network"]},
        )
    )
    monitor.task_heartbeat("still running")
    monitor.task_stop("completed")


if __name__ == "__main__":
    main()
