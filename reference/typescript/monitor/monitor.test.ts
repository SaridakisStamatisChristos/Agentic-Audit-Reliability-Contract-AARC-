import assert from "node:assert/strict";

import {
  Monitor,
  ToolAuthorizationError,
  verifyTrace,
} from "./monitor";

const monitor = new Monitor(
  "agent-ts",
  "task-ts",
  "retrieve a record",
  { policy_id: "ts-eval", constraints: ["lookup-only"] },
  "actor",
  ["lookup"],
  "run-ts",
);

monitor.taskStart();
monitor.snapshotState(
  { record: "A" },
  {},
  { value: 0.9, uncertainty: 0.1, evidence_coverage: 1.0 },
  ["fixture assumption"],
  ["fixture://record/A"],
);
monitor.recordApprovalDecision(
  "actor-1",
  "critic-1",
  "judge-1",
  { tool: "lookup" },
  { result: "no blocking issue" },
  "approved",
  ["fixture://policy/ts-eval"],
);
const permit = monitor.requestTool("lookup", { record: "A" });
monitor.recordToolResult(permit, { value: 7 });
monitor.taskStop("ok");

assert.doesNotThrow(() => verifyTrace(monitor.events, ["lookup"]));

const denied = new Monitor(
  "agent-ts-denied",
  "task-ts-denied",
  "read only",
  { policy_id: "deny-eval" },
  "actor",
  ["lookup"],
  "run-ts-denied",
);
denied.taskStart();
assert.throws(
  () => denied.requestTool("delete", { record: "A" }),
  ToolAuthorizationError,
);
assert.equal(denied.events.at(-1)?.event_type, "tool.denied");

const forged = structuredClone(monitor.events);
const approval = forged.find(
  (event) => event.event_type === "approval.decided",
);
assert.ok(approval);
approval.payload.judge_id = approval.payload.actor_id;
assert.throws(() => verifyTrace(forged, ["lookup"]));

console.log("TypeScript AARC v1.1.0 conformance smoke tests passed");
