# Agentic Reliability Framework
## Normative Requirements Index v1.0.5

This document enumerates the normative requirements that govern ARF-compliant
systems. "MUST", "SHOULD", and "MAY" are interpreted as described in RFC 2119.

## 1. Conformance

- **NR-1**: An ARF implementation **MUST** emit a runtime contract event stream
  that captures task boundaries, state vectors, and error states.
- **NR-2**: Implementations **MUST** produce an Agentic Change Journal (ACJ)
  entry for each material change in behavior, configuration, or policy.
- **NR-3**: Implementations **MUST** maintain a patch ledger that is append-only
  and uniquely identifies each patch.
- **NR-4**: Implementations **MUST** preserve causal ordering between runtime
  events, ACJ entries, and patch ledger records.
- **NR-5**: Implementations **MUST** retain a stable identifier for the agent
  instance across the lifespan of a task.

## 2. Runtime Contract Requirements

- **NR-6**: The runtime contract stream **MUST** include start, heartbeat, and
  stop events for each task or session.
- **NR-7**: Every runtime event **MUST** include a timestamp with timezone
  offset or UTC indicator.
- **NR-8**: State vector snapshots **MUST** include at minimum the fields
  defined by `spec/AARC_STATE_VECTOR.schema.v1_0_5.json`.
- **NR-9**: When a task fails, the runtime contract **MUST** record the failure
  classification and a remediation outcome.

## 3. Agentic Change Journal (ACJ) Requirements

- **NR-10**: ACJ entries **MUST** include a unique identifier, change summary,
  scope, and evidence references.
- **NR-11**: ACJ entries **SHOULD** include pre-change and post-change state
  vector hashes.
- **NR-12**: ACJ entries **MUST** be immutable once published.

## 4. Patch Ledger Requirements

- **NR-13**: Patch ledger records **MUST** include a patch identifier, parent
  identifier (if applicable), applied timestamp, and outcome status.
- **NR-14**: Patch ledger records **MUST** reference the ACJ entry that
  motivated the patch.
- **NR-15**: Patch ledger records **SHOULD** include cryptographic integrity
  metadata (hashes or signatures).

## 5. Security and Privacy

- **NR-16**: Implementations **MUST** redact or tokenize sensitive data in
  runtime events and ACJ entries.
- **NR-17**: Access to runtime logs and patch ledgers **MUST** be controlled
  through authenticated mechanisms.
- **NR-18**: Implementations **SHOULD** support log export with verifiable
  integrity guarantees.

## 6. Interoperability

- **NR-19**: Implementations **MUST** serialize logs in a machine-readable
  format (JSON or equivalent).
- **NR-20**: Implementations **MAY** provide adapters for existing observability
  stacks as long as the ARF-required fields are preserved.
