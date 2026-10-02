# Agentic Audit & Reliability Contract (AARC)

**Repository release:** v1.1.2  
**Normative contract/specification:** v1.1.0

AARC is a machine-verifiable execution contract for tool-using AI agents. It standardizes the observable evidence needed to verify runtime ordering, immutable intent anchors, tool authorization, separated approval identities, and change provenance without depending on hidden chain-of-thought.

Main now includes the **v1.1.2 publication-metadata patch**. The archived preprint remains **v1.1.1**, built on the unchanged **v1.1.0 normative contract and executable artifact**:

> **AARC: A Machine-Verifiable Audit and Reliability Contract for Tool-Using AI Agents**
>
> Zenodo preprint v1.1.1: **https://doi.org/10.5281/zenodo.23107336**  
> Author ORCID: **https://orcid.org/0009-0002-1699-2043**

## What v1.1.0 adds

- **Explicit wire schemas** for runtime events and State Vector snapshots.
- **RFC 8785 JCS + SHA-256** event commitments for cross-language deterministic hashing.
- **Immutable role/objective/policy anchors** checked on every event.
- **Fail-closed Tool Gateway semantics** with request → authorize/deny → execute permit binding.
- **Separated Decision Validation (SDV)** for Actor–Critic–Judge receipts without colliding with the existing **ACJ = Agentic Change Journal** acronym.
- **Executable Python and TypeScript reference monitors**.
- **Adversarial conformance tests** including rehashed semantic forgeries.
- **Cross-language canonicalization vectors**.
- **Scaling benchmark** for commit and verification overhead.
- **Fail-closed publication CI** for schemas, tests, TypeScript, BibTeX, PDF build, spec hashing, and arXiv packaging.

## Repository layout

```text
spec/                         Normative versioned AARC contracts and schemas
reference/python/             Executable Python monitor + verifier
reference/typescript/         Executable TypeScript monitor + verifier
evaluation/                   Fault-injection and scaling benchmarks
tests/                        Python conformance tests
paper/                        Publication source and bibliography
scripts/                      Reproducible build and packaging utilities
.github/workflows/ci.yml      Release/conformance gate
```

## Conformance quick start

Python:

```bash
python -m pip install -e ".[test,paper]"
./scripts/verify_schema.sh
pytest -q
python -m evaluation.run_conformance_benchmark
python -m evaluation.run_performance_benchmark
```

TypeScript:

```bash
npm install --ignore-scripts --no-audit --no-fund
npm run test:ts
```

Publication build:

```bash
python -m pip install matplotlib
./scripts/build_pdf.sh
./scripts/make_arxiv_zip.sh
```

## Scope

AARC conformance means the externally observable runtime trace satisfies the specified structural and semantic invariants. It does **not** by itself prove factual correctness, policy quality, signer authenticity, or general agent safety. Production deployments that require provenance authenticity should combine the AARC hash chain with authenticated signatures, protected checkpoints, or a transparency mechanism.

## Versioning

v1.1.0 is a semantic upgrade from v1.0.5. Existing v1.0.5 files remain in the repository as historical artifacts. New incompatible semantics must use a new specification version rather than silently changing the meaning of an existing version.

v1.1.1 is a **paper and publication-metadata patch only**. It adds literature positioning for Cordon, Mnemosyne/ATP, and the September 30, 2026 Runtime Assurance Contract paper. It does **not** change the normative runtime contract, schemas, reference monitors, conformance semantics, or September 25 evaluation results.

v1.1.2 is a **repository metadata-only patch** that records the Zenodo preprint DOI and author ORCID. It does not modify the v1.1.1 paper file, normative specifications, runtime schemas, reference monitors, conformance logic, or evaluation results.

The active normative version is declared in `SPEC_VERSION` and remains **1.1.0**. Publication builds compute a deterministic hash over that normative spec set and embed the hash in the PDF.

## Historical name

The project was previously referred to internally as **ARF**. It was renamed to **AARC** to avoid naming collision.
