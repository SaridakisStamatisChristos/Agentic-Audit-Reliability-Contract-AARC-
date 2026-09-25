# AARC Patch Ledger v1.1.0

The patch ledger is an append-only operational record of mitigations and changes applied to an AARC-controlled system.

## 1. Required record fields

Each record MUST include:

- `patch_id`
- `timestamp`
- `applied_by`
- `status` in `applied | rolled_back | superseded | failed`
- `summary`
- `artifact_refs`
- `verification_refs`

When motivated by an Agentic Change Journal entry, the record MUST include `acj_id`.

## 2. Append-only history

Rollback and supersession MUST be represented by new records. Historical records MUST NOT be rewritten.

## 3. Integrity

Records SHOULD include `prev_patch_hash` and `patch_hash`, or equivalent signed/transparency-log evidence. As with the runtime event chain, a bare hash chain is an integrity mechanism, not proof of signer identity.

## 4. Verification

An applied patch SHOULD identify the conformance tests, benchmark cases, or deployment checks executed after application. A release MUST NOT cite a patch as verified when the referenced checks failed or were not run.
