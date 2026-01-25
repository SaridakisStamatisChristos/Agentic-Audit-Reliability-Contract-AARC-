# ARF Patch Ledger v1.0.4

The patch ledger is an append-only log of fixes, mitigations, and code or
configuration changes applied to an ARF-controlled system. It provides an audit
trail that links remediation actions to the evidence captured in runtime
contract events and the Agentic Change Journal (ACJ).

## 1. Ledger Record Fields

Each patch ledger record MUST include:

- `patch_id`: Unique identifier for the patch.
- `parent_patch_id`: Optional identifier when the patch supersedes another.
- `timestamp`: ISO 8601 timestamp of application.
- `applied_by`: Identifier of the actor or automation applying the patch.
- `status`: Applied, rolled back, or superseded.
- `acj_id`: Identifier of the corresponding ACJ entry.
- `summary`: Human-readable description of the patch.

Optional fields include:

- `artifacts`: References to code changes, configuration diffs, or binaries.
- `verification`: Tests or checks executed after application.
- `integrity`: Hashes or signatures for record integrity.

## 2. Append-Only Requirements

The ledger MUST be append-only. If a patch is superseded or rolled back, a new
record MUST be added that references the superseded patch in `parent_patch_id`.

## 3. Integrity and Retention

Implementations SHOULD compute a running hash over the ledger records. Ledger
files SHOULD be retained for the lifetime of the system or for the retention
policy required by governance.

## 4. Serialization

Patch ledger records MUST be serialized as JSON lines or a comparable
record-oriented format. The ledger SHOULD be machine-readable without schema
migration for all v1.x releases.
