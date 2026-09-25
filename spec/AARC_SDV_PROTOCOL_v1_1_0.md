# AARC Separated Decision Validation (SDV) Protocol v1.1.0

This protocol standardizes the optional Actor--Critic--Judge review pattern without overloading the AARC acronym **ACJ**, which is reserved for the Agentic Change Journal.

## 1. Roles

- **Actor**: proposes an action, answer, plan, or change.
- **Critic**: attempts to identify evidence gaps, contradictions, boundary violations, and unsupported assumptions.
- **Judge**: makes the approval decision from the proposal, critique, policy state, and evidence references.

For an approval decision, `actor_id`, `critic_id`, and `judge_id` MUST be pairwise distinct.

## 2. Approval receipt

An approved decision MUST record:

- `proposal_hash`
- `critique_hash`
- `actor_id`
- `critic_id`
- `judge_id`
- `decision=approved`
- one or more `evidence_refs`

A rejected decision MAY omit evidence references but MUST retain proposal and critique digests.

## 3. Security property

SDV prevents a single runtime identity from unilaterally creating a conforming approval receipt. It does not guarantee independence when several logical roles are controlled by the same compromised principal. Deployments requiring organizational separation SHOULD bind role identities to independently authenticated principals or services.
