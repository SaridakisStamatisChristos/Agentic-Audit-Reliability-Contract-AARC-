# Agentic Reliability Framework

The Agentic Reliability Framework (ARF) defines a lightweight, auditable contract
for agentic systems that need consistent runtime telemetry, repair tracking, and
verifiable change logs. This repository contains the normative specifications,
reference monitor implementations, and a companion paper for the v1.0.4
specification series.

## What is included

- **Specs**: Normative requirements, runtime contract, patch ledger, and ACJ
  protocol definitions. See the `spec/` directory.
- **Reference implementations**: Minimal monitors in Python and TypeScript under
  `reference/`.
- **Paper**: A short overview of the framework with citations in `paper/`.

## Versioning

All documents in this repository are aligned to **v1.0.4**. Backwards-incompatible
changes must increment the major or minor spec version.

## Repository layout

```
./spec/                      Normative specifications
./reference/                 Reference monitor implementations
./paper/                     Companion paper
```

## Contributing

When updating the specification, ensure the normative requirements index is
updated and any reference implementation changes are reflected in the paper.
