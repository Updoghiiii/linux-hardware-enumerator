#!/usr/bin/env python3
"""Verify the package CLI emits clean machine-readable JSON."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def main() -> int:
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(SRC)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "hw_enum",
            "--json",
            "--sysfs-limit",
            "1",
        ],
        cwd=ROOT,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    if result.returncode != 0:
        print("FAIL: JSON CLI exited unsuccessfully")
        print(result.stderr)
        return 1

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        print(f"FAIL: JSON CLI emitted non-JSON output: {error}")
        print(result.stdout)
        return 1

    if payload.get("schema") != "linux-hardware-enumerator":
        print("FAIL: JSON CLI schema identifier")
        return 1

    objects = payload.get("sysfs", {}).get("objects", [])
    if not isinstance(objects, list) or len(objects) > 1:
        print("FAIL: JSON CLI did not honor sysfs bound")
        return 1

    if result.stderr.strip():
        print("FAIL: JSON CLI emitted unexpected stderr")
        print(result.stderr)
        return 1

    print("PASS: module CLI emits clean JSON only")
    print("PASS: module CLI honors sysfs inventory bound")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
