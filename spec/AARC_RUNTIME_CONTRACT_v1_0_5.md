# ARF Runtime Contract v1.0.5

The runtime contract defines the minimal event stream required for reliable,
observable agent execution. It establishes the event types, required fields,
and lifecycle semantics for ARF-compliant systems.

## 1. Event Types

ARF-compliant systems MUST emit the following event types:

- `task.start`: Signals the beginning of a task or session.
- `task.heartbeat`: Periodic indicator that the task is still running.
- `task.stop`: Signals normal completion of a task.
- `task.fail`: Signals an abnormal termination or failure.
- `task.remediate`: Records remediation actions or recovery attempts.
- `state.snapshot`: Captures a state vector snapshot.

## 2. Required Fields

Each runtime event MUST include:

- `event_id`: Globally unique identifier.
- `event_type`: One of the types listed above.
- `timestamp`: ISO 8601 timestamp with timezone offset or `Z` suffix.
- `agent_id`: Stable identifier for the agent instance.
- `task_id`: Identifier for the task or session.
- `sequence`: Monotonic sequence number within the task.

## 3. State Vector Integration

State vector snapshots MUST conform to
`spec/AARC_STATE_VECTOR.schema.v1_0_5.json` and include:

- `inputs`: A summary of inputs or intents.
- `outputs`: A summary of outputs produced so far.
- `tools`: Tools invoked and their outcomes.
- `confidence`: Agent confidence or uncertainty indicators.
- `policy`: Policy or constraint references.

Snapshots SHOULD be emitted at task start, before and after tool calls, and
whenever the policy or plan materially changes.

## 4. Failure and Remediation

When emitting `task.fail`, the event MUST include:

- `failure_class`: A stable classification identifier.
- `failure_summary`: A human-readable summary.
- `impact`: Observed or expected impact.

Remediation events MUST include:

- `remediation_id`: Unique identifier for the remediation attempt.
- `strategy`: Strategy category (rollback, retry, escalation, etc.).
- `outcome`: Success, partial success, or failure.

## 5. Integrity Guarantees

Implementations SHOULD provide integrity metadata for batches of events,
including event hashes or signatures. When integrity metadata is present, the
monitor MUST record it alongside the events in the patch ledger.

## 6. Export Formats

The runtime contract stream MUST be serializable as JSON lines or an equivalent
record-oriented format. Binary or compressed formats are permitted as long as
lossless transformation back to JSON is possible.
