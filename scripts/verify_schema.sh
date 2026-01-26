#!/usr/bin/env bash
set -euo pipefail

schema_path="spec/AARC_STATE_VECTOR.schema.v1_0_5.json"

if [[ ! -f "$schema_path" ]]; then
  echo "Schema not found: $schema_path" >&2
  exit 1
fi

python - <<'PY'
import json
from pathlib import Path

schema_path = Path("spec/AARC_STATE_VECTOR.schema.v1_0_5.json")
data = json.loads(schema_path.read_text())
if not isinstance(data, dict):
    raise SystemExit("Schema root must be an object")
if data.get("$schema") is None:
    raise SystemExit("Schema missing $schema key")
print(f"Schema sanity check passed: {schema_path}")
PY
