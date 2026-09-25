# Agentic Audit & Reliability Contract
## Normative Requirements Index v1.1.0

"MUST", "SHOULD", and "MAY" are interpreted as described by BCP 14 (RFC 2119 and RFC 8174).

### Trace and lifecycle
- **NR-1**: A run MUST begin with `task.start`.
- **NR-2**: A completed run MUST end with exactly one `task.stop` or `task.fail`.
- **NR-3**: Event sequence numbers MUST be contiguous and begin at 1.
- **NR-4**: Runtime events MUST validate against the v1.1.0 runtime-event schema.
- **NR-5**: State snapshots MUST validate against the v1.1.0 state-vector schema.

### Integrity and anchors
- **NR-6**: Every event MUST contain a SHA-256 `event_hash`.
- **NR-7**: Every non-genesis event MUST reference the prior committed event hash.
- **NR-8**: Role, objective, and policy anchors MUST remain immutable for a run.
- **NR-9**: Integrity-chain verification MUST fail closed on mutation, deletion, duplication, or reordering that breaks the contract.
- **NR-10**: Deployments claiming signer authenticity MUST use an authenticated signature or externally trusted checkpoint in addition to the hash chain.

### Tool side effects
- **NR-11**: A tool request MUST receive an explicit authorize or deny decision before execution.
- **NR-12**: A denied request MUST NOT produce a conforming execution event.
- **NR-13**: A tool execution MUST reference a valid authorization permit and match its tool identity.
- **NR-14**: The authorization decision MUST be enforced outside model-generated text.

### Separated decision validation
- **NR-15**: Positive approvals using SDV MUST bind proposal and critique digests.
- **NR-16**: Actor, Critic, and Judge identities MUST be pairwise distinct for a positive approval.
- **NR-17**: Positive approvals MUST reference evidence.
- **NR-18**: The acronym ACJ MUST refer only to Agentic Change Journal in normative AARC documents.

### Change provenance
- **NR-19**: Material policy, model, prompt, configuration, or code changes MUST be representable as Agentic Change Journal entries.
- **NR-20**: Published ACJ entries MUST be immutable; corrections MUST supersede rather than mutate.
- **NR-21**: Applied remediation patches MUST link to motivating evidence or an ACJ entry.

### Privacy and interoperability
- **NR-22**: Sensitive values SHOULD be represented by digests, tokens, or redacted summaries unless raw retention is explicitly required.
- **NR-23**: AARC logs MUST be serializable as lossless JSON records.
- **NR-24**: Implementations SHOULD expose versioned adapters rather than silently changing event semantics.
- **NR-25**: A conforming implementation MUST pass the repository's positive and adversarial conformance suite for the claimed specification version.
