#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from evaluation.run_conformance_benchmark import healthy_trace

root = Path(".")
state_path = root / "spec" / "AARC_STATE_VECTOR.schema.v1_1_0.json"
event_path = root / "spec" / "AARC_RUNTIME_EVENT.schema.v1_1_0.json"

state_schema = json.loads(state_path.read_text(encoding="utf-8"))
event_schema = json.loads(event_path.read_text(encoding="utf-8"))

Draft202012Validator.check_schema(state_schema)
Draft202012Validator.check_schema(event_schema)

format_checker = FormatChecker()
state_validator = Draft202012Validator(
    state_schema,
    format_checker=format_checker,
)
event_validator = Draft202012Validator(
    event_schema,
    format_checker=format_checker,
)

events = healthy_trace()
for event in events:
    event_validator.validate(event)

snapshot = next(
    event["payload"]
    for event in events
    if event["event_type"] == "state.snapshot"
)
state_validator.validate(snapshot)

print("AARC v1.1.0 schemas and positive conformance fixture validated")
PY
