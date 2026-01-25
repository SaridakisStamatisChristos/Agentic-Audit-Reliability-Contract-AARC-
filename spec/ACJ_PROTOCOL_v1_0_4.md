# Agentic Change Journal (ACJ) Protocol v1.0.4

The Agentic Change Journal (ACJ) Protocol defines how agentic systems record
material changes to behavior, configuration, policy, or runtime posture. The
protocol ensures that changes are traceable, reviewable, and linked to runtime
telemetry.

## 1. ACJ Entry Structure

Each ACJ entry MUST include:

- `acj_id`: Unique identifier.
- `timestamp`: ISO 8601 timestamp.
- `agent_id`: Identifier of the agent responsible for the change.
- `change_type`: Policy, configuration, model, prompt, or code.
- `summary`: Human-readable summary.
- `scope`: Impacted components or capabilities.
- `evidence`: References to runtime events, logs, or external tickets.

Recommended fields:

- `pre_state_hash`: Hash of the prior state vector.
- `post_state_hash`: Hash of the new state vector.
- `reviewer`: Reviewer identifier when human approval is required.
- `risk_level`: Low, medium, or high.

## 2. Publication Rules

ACJ entries MUST be immutable after publication. If corrections are necessary,
a new ACJ entry MUST be created that references the superseded entry.

## 3. Linking Requirements

Every ACJ entry MUST be linkable to:

- One or more runtime contract events that provide evidence.
- Patch ledger records that apply the change, when applicable.

## 4. Serialization

ACJ entries MUST be serialized in JSON or equivalent machine-readable format.
Implementations SHOULD provide a stable schema with versioned field names.
