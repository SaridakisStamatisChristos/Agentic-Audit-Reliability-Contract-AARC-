# AARC Runtime Contract v1.1.0

AARC v1.1.0 defines a fail-closed runtime contract for auditable tool-using agents. Conformance is decided from committed runtime events and explicit policy state, not hidden chain-of-thought.

## 1. Canonical event stream

A conforming run MUST serialize events that validate against `AARC_RUNTIME_EVENT.schema.v1_1_0.json`. Event sequence numbers MUST be contiguous and begin at 1.

The first event MUST be `task.start`. A completed trace MUST end in exactly one terminal event: `task.stop` or `task.fail`. No event may follow a terminal event.

## 2. Integrity chain

Every event MUST include `prev_event_hash` and `event_hash`.

- The first event MUST use 64 zeroes for `prev_event_hash`.
- For event (e_i), `prev_event_hash` MUST equal the committed `event_hash` of (e_{i-1}).
- `event_hash` MUST be SHA-256 over deterministic canonical JSON of the event with the `event_hash` field omitted.

A hash chain detects accidental corruption and post-commit mutation relative to a trusted checkpoint. It does **not** by itself provide signer authenticity. Deployments that require non-repudiation SHOULD externally sign or transparency-log checkpoints.

## 3. Immutable anchors

The `role_hash`, `objective_hash`, and `policy_hash` established by `task.start` MUST remain byte-identical for the lifetime of the run. Any drift MUST cause verification failure and SHOULD revoke side-effect capabilities.

## 4. Tool authorization

Tool execution is fail-closed:

1. `tool.requested` records the proposed tool and argument digest.
2. A policy gate emits exactly one matching `tool.authorized` or `tool.denied`.
3. `tool.executed` MUST reference a valid `tool.authorized` permit event and MUST match the authorized tool.
4. A denied request MUST NOT produce `tool.executed`.

The policy gate MAY be implemented using allowlists, capability tokens, a policy engine, or an external authorization service. The authorization decision MUST be made outside the model-generated text channel.

## 5. Separated decision validation

Where a deployment uses Actor--Critic--Judge review, the runtime event is `approval.decided`. A positive approval MUST record distinct Actor, Critic, and Judge identifiers, a proposal digest, a critique digest, and at least one evidence reference. A model or process MAY occupy multiple roles across different tasks, but MUST NOT self-approve within one approval decision.

The acronym **ACJ is reserved for Agentic Change Journal** in AARC specifications; Actor--Critic--Judge is written out or described as separated decision validation (SDV).

## 6. State snapshots

`state.snapshot` payloads MUST validate against `AARC_STATE_VECTOR.schema.v1_1_0.json`. The state vector repeats immutable anchors and trace coordinates so a snapshot can be audited independently of private chain-of-thought.

## 7. Fail-closed verification

A verifier MUST reject traces with broken hashes, non-contiguous ordering, anchor drift, unauthorized tool execution, invalid approval separation, or invalid lifecycle termination.

Conformance is a property of the externally observable execution contract. AARC does not claim that these checks establish semantic correctness of model reasoning.
