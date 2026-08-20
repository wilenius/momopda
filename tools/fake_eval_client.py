#!/usr/bin/env python3
"""Deterministic JSON-event client used by evaluation harness tests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time


def emit(event: dict[str, object]) -> None:
    print(json.dumps(event, sort_keys=True), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument(
        "--outcome",
        choices=("success", "control-file", "nonzero", "timeout", "malformed"),
        required=True,
    )
    args = parser.parse_args()

    emit({"type": "step_start", "part": {"type": "step-start"}})
    if args.outcome == "timeout":
        time.sleep(60)
        return 0
    if args.outcome == "malformed":
        print("not-json", flush=True)
        return 0
    if args.outcome == "nonzero":
        print("deterministic fake client failure", file=sys.stderr)
        return 7

    (args.workspace / "fake-client.txt").write_text("deterministic edit\n", encoding="utf-8")
    if args.outcome == "control-file":
        (args.workspace / "phpunit.xml").write_text("<phpunit/>\n", encoding="utf-8")
        (args.workspace / "classes").mkdir(exist_ok=True)
        (args.workspace / "classes" / ".moodle-plugin-ci.yml").write_text(
            "codechecker: false\n",
            encoding="utf-8",
        )
    emit(
        {
            "type": "tool_use",
            "part": {
                "type": "tool",
                "tool": "fake_edit",
                "state": {"status": "completed"},
            },
        }
    )
    emit(
        {
            "type": "step_finish",
            "part": {
                "type": "step-finish",
                "reason": "stop",
                "tokens": {
                    "input": 10,
                    "output": 5,
                    "reasoning": 0,
                    "cache": {"read": 0, "write": 0},
                },
                "cost": 0,
            },
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
