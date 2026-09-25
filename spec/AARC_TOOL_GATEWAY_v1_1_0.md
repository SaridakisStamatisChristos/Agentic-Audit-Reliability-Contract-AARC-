# AARC Tool Gateway Contract v1.1.0

The Tool Gateway is the side-effect enforcement boundary for AARC deployments. It mediates proposed tool actions before execution and emits authorization evidence into the runtime trace.

## 1. Fail-closed semantics

A gateway MUST deny execution unless it can establish all required authorization inputs. Missing policy state, malformed arguments, unknown tool identity, stale permits, and verifier errors MUST resolve to denial rather than implicit allow.

## 2. Request and permit binding

An authorization decision MUST bind:

- the exact `tool_name`;
- a digest of canonicalized arguments;
- the current immutable `policy_hash`;
- the originating `request_event_id`; and
- a unique permit identifier or authorization-event identifier.

A permit MUST NOT authorize a different tool, argument digest, task, run, or policy version.

## 3. Enforcement location

Authorization MUST be evaluated outside the model-generated text channel. The model MAY request a tool but MUST NOT be authoritative for whether the request is permitted.

## 4. Revocation

Deployments SHOULD revoke outstanding permits when the task becomes terminal, policy verification fails, anchor drift is detected, or an operator kill-switch is activated.

## 5. Policy-engine independence

AARC does not prescribe a policy language. The gateway MAY use static allowlists, capability systems, ABAC/RBAC engines, declarative policy languages, SMT-backed authorization, or external policy decision points. AARC standardizes the observable authorization evidence and binding semantics.
