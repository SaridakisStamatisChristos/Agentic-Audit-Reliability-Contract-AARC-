# Agentic Change Journal (ACJ) Protocol v1.1.0

The Agentic Change Journal records material changes to behavior, configuration, policy, model, prompt, code, or runtime posture. ACJ is change provenance; it is not the Actor--Critic--Judge validation pattern.

## 1. Required fields

Each published ACJ entry MUST include:

- `acj_id`
- `timestamp`
- `agent_id` or authenticated principal identifier
- `change_type`
- `summary`
- `scope`
- `evidence_refs`
- `pre_state_hash` when a prior state exists
- `post_state_hash`
- `spec_version`

## 2. Immutability

Published ACJ entries MUST NOT be edited in place. Corrections MUST be represented by a new entry containing `supersedes_acj_id`.

## 3. Runtime linkage

A material change SHOULD reference the runtime events, issue, pull request, deployment record, evaluation artifact, or incident that motivated it. Applied patches SHOULD reference their ACJ entry.

## 4. Integrity

Implementations SHOULD hash-chain or sign journal entries. Hash chaining provides mutation evidence relative to a trusted checkpoint; signatures or an external transparency service are required when signer authenticity is claimed.

## 5. Privacy

Evidence references SHOULD point to redacted or access-controlled artifacts when raw telemetry contains secrets, personal data, or proprietary content.
