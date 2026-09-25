/* AARC v1.1.0 executable reference monitor for TypeScript. */

import { createHash, randomUUID } from "node:crypto";
import canonicalize from "canonicalize";

type JsonObject = Record<string, unknown>;
type EventRecord = {
  event_id: string;
  event_type: string;
  timestamp: string;
  agent_id: string;
  task_id: string;
  run_id: string;
  sequence: number;
  anchors: {
    role_hash: string;
    objective_hash: string;
    policy_hash: string;
  };
  prev_event_hash: string;
  event_hash: string;
  payload: JsonObject;
};

export const ZERO_HASH = "0".repeat(64);
const TERMINAL_EVENTS = new Set(["task.stop", "task.fail"]);

export class TraceVerificationError extends Error {}
export class ToolAuthorizationError extends Error {}

export function canonicalJson(value: unknown): string {
  const encoded = canonicalize(value);
  if (encoded === undefined) {
    throw new Error("value is not representable in RFC 8785 JCS");
  }
  return encoded;
}

export function sha256Hex(value: unknown): string {
  const text = typeof value === "string" ? value : canonicalJson(value);
  return createHash("sha256").update(text, "utf8").digest("hex");
}

export function computeEventHash(event: EventRecord | JsonObject): string {
  const material = { ...(event as JsonObject) };
  delete material.event_hash;
  return sha256Hex(material);
}

export type ToolPermit = {
  toolName: string;
  requestEventId: string;
  permitEventId: string;
};

export class Monitor {
  private sequence = 0;
  readonly events: EventRecord[] = [];
  readonly runId: string;
  readonly anchors: EventRecord["anchors"];
  private readonly allowedTools: Set<string>;

  constructor(
    readonly agentId: string,
    readonly taskId: string,
    readonly objective: string,
    readonly policy: JsonObject,
    readonly role = "actor",
    allowedTools: Iterable<string> = [],
    runId?: string,
    readonly rootAgentId = agentId,
    readonly parentAgentId: string | null = null,
  ) {
    if (!agentId || !taskId || !objective || !role) {
      throw new Error("agentId, taskId, objective, and role are required");
    }
    this.runId = runId ?? randomUUID();
    this.allowedTools = new Set(allowedTools);
    this.anchors = {
      role_hash: sha256Hex(role),
      objective_hash: sha256Hex(objective),
      policy_hash: sha256Hex(policy),
    };
  }

  private emit(eventType: string, payload: JsonObject = {}): EventRecord {
    if (
      this.events.length > 0 &&
      TERMINAL_EVENTS.has(this.events[this.events.length - 1].event_type)
    ) {
      throw new Error("cannot emit after a terminal event");
    }
    this.sequence += 1;
    const event = {
      event_id: randomUUID(),
      event_type: eventType,
      timestamp: new Date().toISOString(),
      agent_id: this.agentId,
      task_id: this.taskId,
      run_id: this.runId,
      sequence: this.sequence,
      anchors: { ...this.anchors },
      prev_event_hash:
        this.events.length > 0
          ? this.events[this.events.length - 1].event_hash
          : ZERO_HASH,
      payload: structuredClone(payload),
      event_hash: "",
    };
    event.event_hash = computeEventHash(event);
    this.events.push(event);
    return structuredClone(event);
  }

  taskStart(metadata: JsonObject = {}): EventRecord {
    if (this.events.length !== 0) {
      throw new Error("task.start must be the first event");
    }
    return this.emit("task.start", {
      schema_version: "1.1.0",
      root_agent_id: this.rootAgentId,
      parent_agent_id: this.parentAgentId,
      role: this.role,
      objective_digest: this.anchors.objective_hash,
      policy_digest: this.anchors.policy_hash,
      ...metadata,
    });
  }

  snapshotState(
    inputs: JsonObject,
    outputs: JsonObject,
    confidence: JsonObject = {},
    assumptions: string[] = [],
    evidenceRefs: string[] = [],
  ): EventRecord {
    const nextSequence = this.sequence + 1;
    return this.emit("state.snapshot", {
      schema_version: "1.1.0",
      identity: {
        agent_id: this.agentId,
        root_agent_id: this.rootAgentId,
        parent_agent_id: this.parentAgentId,
        role: this.role,
        role_hash: this.anchors.role_hash,
      },
      intent: {
        objective_hash: this.anchors.objective_hash,
        policy_hash: this.anchors.policy_hash,
      },
      trace: {
        run_id: this.runId,
        task_id: this.taskId,
        step_id: `step-${nextSequence}`,
        sequence: nextSequence,
        parent_event_hash:
          this.events.length > 0
            ? this.events[this.events.length - 1].event_hash
            : ZERO_HASH,
      },
      inputs,
      outputs,
      tools: [],
      confidence,
      policy: this.policy,
      assumptions,
      evidence_refs: evidenceRefs,
    });
  }

  requestTool(toolName: string, args: JsonObject): ToolPermit {
    const argumentsDigest = sha256Hex(args);
    const request = this.emit("tool.requested", {
      tool_name: toolName,
      arguments_digest: argumentsDigest,
    });
    const decision = {
      tool_name: toolName,
      request_event_id: request.event_id,
      arguments_digest: argumentsDigest,
      policy_hash: this.anchors.policy_hash,
    };
    if (!this.allowedTools.has(toolName)) {
      this.emit("tool.denied", decision);
      throw new ToolAuthorizationError(`tool denied by policy: ${toolName}`);
    }
    const permit = this.emit("tool.authorized", decision);
    return {
      toolName,
      requestEventId: request.event_id,
      permitEventId: permit.event_id,
    };
  }

  recordToolResult(
    permit: ToolPermit,
    result: unknown,
    failed = false,
  ): EventRecord {
    return this.emit(failed ? "tool.failed" : "tool.executed", {
      tool_name: permit.toolName,
      request_event_id: permit.requestEventId,
      permit_event_id: permit.permitEventId,
      result_digest: sha256Hex(result),
    });
  }

  recordApprovalDecision(
    actorId: string,
    criticId: string,
    judgeId: string,
    proposal: unknown,
    critique: unknown,
    decision: "approved" | "rejected",
    evidenceRefs: string[],
  ): EventRecord {
    if (
      decision === "approved" &&
      new Set([actorId, criticId, judgeId]).size !== 3
    ) {
      throw new Error(
        "positive approval requires pairwise-distinct Actor/Critic/Judge",
      );
    }
    if (decision === "approved" && evidenceRefs.length === 0) {
      throw new Error("positive approval requires evidence");
    }
    return this.emit("approval.decided", {
      actor_id: actorId,
      critic_id: criticId,
      judge_id: judgeId,
      proposal_hash: sha256Hex(proposal),
      critique_hash: sha256Hex(critique),
      decision,
      evidence_refs: evidenceRefs,
    });
  }

  taskStop(summary?: string): EventRecord {
    return this.emit("task.stop", summary ? { summary } : {});
  }

  taskFail(
    failureClass: string,
    failureSummary: string,
    impact: string,
  ): EventRecord {
    return this.emit("task.fail", {
      failure_class: failureClass,
      failure_summary: failureSummary,
      impact,
    });
  }
}

export function verifyTrace(
  events: EventRecord[],
  allowedTools?: Iterable<string>,
): void {
  if (events.length === 0) {
    throw new TraceVerificationError("empty trace");
  }
  if (events[0].event_type !== "task.start") {
    throw new TraceVerificationError("trace must begin with task.start");
  }

  const expectedAnchors = canonicalJson(events[0].anchors);
  const allowed = allowedTools ? new Set(allowedTools) : undefined;
  const permits = new Map<
    string,
    { requestEventId: string; toolName: string }
  >();
  const denied = new Set<string>();
  let previousHash = ZERO_HASH;
  let terminalSeen = false;

  events.forEach((event, offset) => {
    const sequence = offset + 1;
    if (terminalSeen) {
      throw new TraceVerificationError("event appears after terminal event");
    }
    if (event.sequence !== sequence) {
      throw new TraceVerificationError("non-contiguous event sequence");
    }
    if (event.prev_event_hash !== previousHash) {
      throw new TraceVerificationError("broken previous-event hash link");
    }
    if (event.event_hash !== computeEventHash(event)) {
      throw new TraceVerificationError("event hash mismatch");
    }
    if (canonicalJson(event.anchors) !== expectedAnchors) {
      throw new TraceVerificationError("immutable anchor drift");
    }

    const payload = event.payload;
    if (event.event_type === "tool.denied") {
      const requestId = payload.request_event_id;
      if (typeof requestId === "string") denied.add(requestId);
    } else if (event.event_type === "tool.authorized") {
      const requestId = payload.request_event_id;
      const toolName = payload.tool_name;
      if (typeof requestId !== "string" || typeof toolName !== "string") {
        throw new TraceVerificationError("malformed tool authorization");
      }
      if (denied.has(requestId)) {
        throw new TraceVerificationError("request both denied and authorized");
      }
      if (allowed && !allowed.has(toolName)) {
        throw new TraceVerificationError(
          "authorization violates verifier policy",
        );
      }
      permits.set(event.event_id, {
        requestEventId: requestId,
        toolName,
      });
    } else if (
      event.event_type === "tool.executed" ||
      event.event_type === "tool.failed"
    ) {
      const permitId = payload.permit_event_id;
      const requestId = payload.request_event_id;
      const toolName = payload.tool_name;
      if (typeof permitId !== "string") {
        throw new TraceVerificationError("tool execution without valid permit");
      }
      const permit = permits.get(permitId);
      if (!permit) {
        throw new TraceVerificationError("tool execution without valid permit");
      }
      if (
        permit.requestEventId !== requestId ||
        permit.toolName !== toolName
      ) {
        throw new TraceVerificationError(
          "tool execution does not match permit",
        );
      }
      if (typeof requestId === "string" && denied.has(requestId)) {
        throw new TraceVerificationError("denied tool request was executed");
      }
      if (
        allowed &&
        typeof toolName === "string" &&
        !allowed.has(toolName)
      ) {
        throw new TraceVerificationError(
          "executed tool violates verifier policy",
        );
      }
    } else if (
      event.event_type === "approval.decided" &&
      payload.decision === "approved"
    ) {
      const ids = new Set([
        payload.actor_id,
        payload.critic_id,
        payload.judge_id,
      ]);
      if (ids.has(undefined) || ids.size !== 3) {
        throw new TraceVerificationError(
          "self-approval or missing SDV identity",
        );
      }
      if (!payload.proposal_hash || !payload.critique_hash) {
        throw new TraceVerificationError(
          "approval missing proposal/critique digest",
        );
      }
      if (
        !Array.isArray(payload.evidence_refs) ||
        payload.evidence_refs.length === 0
      ) {
        throw new TraceVerificationError("approval missing evidence");
      }
    }

    if (TERMINAL_EVENTS.has(event.event_type)) {
      terminalSeen = true;
    }
    previousHash = event.event_hash;
  });

  if (!TERMINAL_EVENTS.has(events[events.length - 1].event_type)) {
    throw new TraceVerificationError("trace is not terminal");
  }
}
