# Reference Implementations

This directory contains minimal reference monitors for the Agentic Reliability
Framework (ARF). The monitors demonstrate how to collect runtime telemetry,
produce ACJ entries, and emit patch ledger records.

## Python

Location: `reference/python/monitor/monitor.py`

The Python monitor provides a small in-process event recorder. It tracks
state-vector snapshots, task boundaries, and recovery actions in a JSON log.

## TypeScript

Location: `reference/typescript/monitor/monitor.ts`

The TypeScript monitor mirrors the Python behavior with a simple event stream
that can be piped to a logging backend.

## Using the reference monitors

Both reference monitors are intentionally small and intended for adaptation.
When integrating into production systems, ensure that:

- State vector snapshots are taken at the entry and exit of each task.
- ACJ events include deterministic identifiers and timestamps.
- Patch ledger entries are signed or otherwise protected against tampering.
