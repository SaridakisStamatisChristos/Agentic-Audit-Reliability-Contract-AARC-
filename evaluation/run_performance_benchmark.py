#!/usr/bin/env python3
"""Microbenchmark AARC v1.1.0 commit and verification overhead.

Results are environment-specific and are emitted as machine-readable JSON.
The paper should identify the runner/environment when quoting these numbers.
"""

from __future__ import annotations

import json
import statistics
import time
from typing import Dict, List

from reference.python.monitor.monitor import Monitor, verify_trace


SIZES = (100, 1000, 5000)
REPEATS = 5


def build_trace(heartbeats: int):
    monitor = Monitor(
        agent_id="perf-agent",
        task_id="perf-task",
        run_id="perf-run",
        objective="measure AARC overhead",
        policy={"policy_id": "perf", "constraints": ["no-tools"]},
    )
    monitor.task_start()
    for index in range(heartbeats):
        monitor.heartbeat(f"hb-{index}")
    monitor.task_stop("done")
    return monitor.events


def median(values: List[float]) -> float:
    return statistics.median(values)


def main() -> int:
    rows: List[Dict[str, float]] = []
    for heartbeats in SIZES:
        commit_times = []
        verify_times = []
        event_count = heartbeats + 2

        for _ in range(REPEATS):
            start = time.perf_counter()
            events = build_trace(heartbeats)
            commit_times.append(time.perf_counter() - start)

            start = time.perf_counter()
            verify_trace(events)
            verify_times.append(time.perf_counter() - start)

        commit_s = median(commit_times)
        verify_s = median(verify_times)
        rows.append(
            {
                "events": event_count,
                "commit_seconds_median": commit_s,
                "verify_seconds_median": verify_s,
                "commit_us_per_event": commit_s * 1_000_000 / event_count,
                "verify_us_per_event": verify_s * 1_000_000 / event_count,
                "commit_events_per_second": event_count / commit_s,
                "verify_events_per_second": event_count / verify_s,
            }
        )

    print(
        json.dumps(
            {
                "spec_version": "1.1.0",
                "repeats": REPEATS,
                "rows": rows,
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
