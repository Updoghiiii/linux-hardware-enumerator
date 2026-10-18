from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from hw_enum.enumerators.audio import enumerate_audio
from hw_enum.enumerators.usb import enumerate_usb
from hw_enum.graph import build_graph, enumerate_graph
from hw_enum.interpretation import interpret_observation
from hw_enum.inventory import collect_inventory
from hw_enum.relationships import walk_observations


SYSFS_BUS = Path("/sys/bus")


def discover_bus_objects() -> list[Path]:
    objects = []

    try:
        buses = sorted(SYSFS_BUS.iterdir())
    except (FileNotFoundError, PermissionError, OSError):
        return objects

    for bus in buses:
        if not bus.is_dir():
            continue

        devices = bus / "devices"

        if not devices.is_dir():
            continue

        try:
            entries = sorted(devices.iterdir())
        except (FileNotFoundError, PermissionError, OSError):
            continue

        for entry in entries:
            objects.append(entry)

    return objects


def enumerate_sysfs() -> None:
    print("\n=== GENERIC SYSFS DISCOVERY ===")

    objects = discover_bus_objects()

    if not objects:
        print("(none or unavailable)")
        return

    print(f"Discovered {len(objects)} bus objects.")

    for target in objects:
        observations = walk_observations(
            target,
            max_depth=5,
        )

        interpretations = [
            interpret_observation(observation)
            for observation in observations
        ]

        graph = build_graph(interpretations)

        if graph.relationships:
            print(f"\n--- {target} ---")
            enumerate_graph(graph)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="linux-hardware-enumerator",
        description=(
            "Collect Linux hardware evidence and emit either human-readable "
            "output or a versioned JSON inventory."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="emit only the machine-readable JSON inventory",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="pretty-print JSON output",
    )
    parser.add_argument(
        "--sysfs-limit",
        type=int,
        default=4096,
        help="maximum generic sysfs bus objects included in JSON output",
    )
    parser.add_argument(
        "--no-sysfs-walk",
        action="store_true",
        help="skip the verbose recursive sysfs graph in human-readable mode",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    if args.json:
        inventory = collect_inventory(sysfs_limit=args.sysfs_limit)
        print(
            json.dumps(
                inventory,
                indent=2 if args.pretty else None,
                sort_keys=args.pretty,
            )
        )
        return 0

    print("Linux Hardware Enumerator")
    print("==========================")

    enumerate_audio()
    print()
    enumerate_usb()

    if not args.no_sysfs_walk:
        enumerate_sysfs()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
