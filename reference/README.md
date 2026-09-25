# AARC Reference Implementations

The Python and TypeScript implementations in this directory are executable reference monitors for **AARC v1.1.0**. They are intended to demonstrate the normative wire semantics and verifier behavior, not to prescribe a production policy engine.

## Implemented guarantees

Both implementations cover:

- RFC 8785 canonical event serialization and SHA-256 commitments;
- contiguous event sequencing and predecessor-hash linkage;
- immutable role/objective/policy anchors;
- State Vector snapshots;
- fail-closed tool authorization with permit-bound execution;
- Actor–Critic–Judge separated approval receipts;
- terminal lifecycle enforcement; and
- offline trace verification.

## Python

Location: `reference/python/monitor/monitor.py`

The Python implementation is the primary executable conformance reference and is exercised by `tests/test_aarc_v1_1.py` plus the fault-injection and performance benchmarks under `evaluation/`.

## TypeScript

Location: `reference/typescript/monitor/monitor.ts`

The TypeScript implementation mirrors the observable contract and includes strict compilation plus conformance smoke tests.

## Canonicalization

Do not replace RFC 8785 JCS with a language-default JSON serializer. Equivalent JSON numbers can serialize differently across runtimes and therefore produce incompatible hashes. The repository includes a cross-language vector specifically to prevent this regression.

## Production integration

A production deployment should treat the monitor and Tool Gateway as trusted enforcement components. Replace the demonstration allow-set with the deployment's policy decision point, and add authenticated checkpoints or signatures when provenance authenticity is required.
