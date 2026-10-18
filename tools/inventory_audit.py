#!/usr/bin/env python3
"""Side-effect-free structural audit for machine-readable inventory."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from hw_enum.inventory import SCHEMA_VERSION, collect_inventory  # noqa: E402


def main() -> int:
    inventory = collect_inventory(sysfs_limit=4)

    if inventory.get("schema") != "linux-hardware-enumerator":
        print("FAIL: inventory schema identifier")
        return 1

    if inventory.get("schema_version") != SCHEMA_VERSION:
        print("FAIL: inventory schema version")
        return 1

    for key in ("collected_at", "host", "sources", "audio", "usb", "sysfs"):
        if key not in inventory:
            print(f"FAIL: inventory missing {key}")
            return 1

    sysfs = inventory.get("sysfs", {})
    objects = sysfs.get("objects", []) if isinstance(sysfs, dict) else []
    if not isinstance(objects, list) or len(objects) > 4:
        print("FAIL: sysfs inventory bounds")
        return 1

    try:
        json.dumps(inventory)
    except (TypeError, ValueError) as error:
        print(f"FAIL: inventory is not JSON serializable: {error}")
        return 1

    print("PASS: versioned machine-readable inventory")
    print("PASS: source availability remains explicit")
    print("PASS: sysfs inventory remains bounded")
    print("PASS: inventory is JSON serializable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
