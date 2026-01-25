/* Minimal ARF reference monitor for TypeScript. */

type Payload = Record<string, unknown>;

type EventRecord = {
  event_id: string;
  event_type: string;
  timestamp: string;
  agent_id: string;
  task_id: string;
  sequence: number;
  payload: Payload;
};

export type StateVector = {
  inputs: Payload;
  outputs: Payload;
  tools: Array<Payload>;
  confidence: Payload;
  policy: Payload;
};

export class Monitor {
  private sequence = 0;
  private events: EventRecord[] = [];

  constructor(private agentId: string, private taskId: string) {}

  private timestamp(): string {
    return new Date().toISOString();
  }

  private nextSequence(): number {
    this.sequence += 1;
    return this.sequence;
  }

  private emit(eventType: string, payload: Payload = {}): EventRecord {
    const event: EventRecord = {
      event_id: crypto.randomUUID(),
      event_type: eventType,
      timestamp: this.timestamp(),
      agent_id: this.agentId,
      task_id: this.taskId,
      sequence: this.nextSequence(),
      payload,
    };
    this.events.push(event);
    process.stdout.write(`${JSON.stringify(event)}\n`);
    return event;
  }

  taskStart(metadata: Payload = {}): EventRecord {
    return this.emit("task.start", metadata);
  }

  taskHeartbeat(note?: string): EventRecord {
    return this.emit("task.heartbeat", note ? { note } : {});
  }

  taskStop(summary?: string): EventRecord {
    return this.emit("task.stop", summary ? { summary } : {});
  }

  taskFail(failureClass: string, failureSummary: string, impact: string): EventRecord {
    return this.emit("task.fail", {
      failure_class: failureClass,
      failure_summary: failureSummary,
      impact,
    });
  }

  remediate(remediationId: string, strategy: string, outcome: string): EventRecord {
    return this.emit("task.remediate", {
      remediation_id: remediationId,
      strategy,
      outcome,
    });
  }

  snapshotState(state: StateVector): EventRecord {
    return this.emit("state.snapshot", state);
  }
}

if (require.main === module) {
  const monitor = new Monitor("agent-demo", "task-demo");
  monitor.taskStart({ intent: "demo run" });
  monitor.snapshotState({
    inputs: { query: "health check" },
    outputs: {},
    tools: [],
    confidence: { level: 0.74 },
    policy: { constraints: ["no-network"] },
  });
  monitor.taskHeartbeat("still running");
  monitor.taskStop("completed");
}
