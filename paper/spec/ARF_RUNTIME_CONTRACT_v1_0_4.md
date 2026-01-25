# ARF Runtime Contract (Paper Appendix) v1.0.4

The runtime contract defines a minimal event stream for agent execution:

- Task lifecycle events (`task.start`, `task.heartbeat`, `task.stop`, `task.fail`).
- State vector snapshots that comply with the v1.0.4 schema.
- Remediation events when recovery is attempted.

The contract guarantees consistent telemetry for auditing and model alignment.
See `spec/ARF_RUNTIME_CONTRACT_v1_0_4.md` for the complete specification.
