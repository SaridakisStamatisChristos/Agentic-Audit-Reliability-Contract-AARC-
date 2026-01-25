#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
spec_version_file="$repo_root/SPEC_VERSION"
schema_path="$repo_root/spec/ARF_STATE_VECTOR.schema.v1_0_4.json"
paper_main="$repo_root/paper/main.tex"
zip_path="$repo_root/dist/ARF_v1_0_4_arxiv.zip"

if [[ ! -f "$spec_version_file" ]]; then
  echo "SPEC_VERSION missing." >&2
  exit 1
fi

expected_version="ARF_VERSION=1.0.4"
if ! grep -Fxq "$expected_version" "$spec_version_file"; then
  echo "SPEC_VERSION does not contain ${expected_version}." >&2
  exit 1
fi

expected_schema="SCHEMA=ARF_STATE_VECTOR.schema.v1_0_4.json"
if ! grep -Fxq "$expected_schema" "$spec_version_file"; then
  echo "SPEC_VERSION does not contain ${expected_schema}." >&2
  exit 1
fi

if [[ ! -f "$schema_path" ]]; then
  echo "Schema file missing: $schema_path" >&2
  exit 1
fi

if [[ "$schema_path" != *v1_0_4* ]]; then
  echo "Schema file name does not include v1_0_4." >&2
  exit 1
fi

if ! rg -n "\\\\input\\{spec_hash\\.tex\\}" "$paper_main" >/dev/null; then
  echo "paper/main.tex does not import spec_hash.tex." >&2
  exit 1
fi

if [[ ! -f "$zip_path" ]]; then
  echo "arXiv zip missing; generating for conformance check."
  "$repo_root/scripts/make_arxiv_zip.sh"
fi

python - <<'PY'
import sys
from pathlib import Path
import zipfile

zip_path = Path("dist/ARF_v1_0_4_arxiv.zip")
required = {
    "main.tex",
    "arf.bib",
    "spec_hash.tex",
    "figures/arf_lifecycle.pdf",
    "figures/arf_architecture.pdf",
    "spec/ARF_STATE_VECTOR.schema.v1_0_4.json",
}

with zipfile.ZipFile(zip_path) as zf:
    names = set(zf.namelist())
missing = sorted(required - names)
if missing:
    sys.exit(f"arXiv zip missing entries: {missing}")
PY

echo "Conformance checks passed."
