"""Machine-readable Linux hardware inventory.

This module composes existing evidence collectors into a bounded, versioned
inventory for other software. It does not claim that every Linux
representation describes a unique physical device; sysfs paths and links remain
evidence about hardware relationships.
"""

from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone
import platform
import socket
from pathlib import Path
from typing import Any

from hw_enum.enumerators.audio import collect_audio
from hw_enum.enumerators.usb import collect_usb
from hw_enum.relationships import collect_relationships


SCHEMA_VERSION = 1
SYSFS_BUS = Path("/sys/bus")


def _source_status(path: Path) -> str:
    """Describe whether a kernel/userspace evidence source can be inspected."""
    try:
        if not path.exists():
            return "unavailable"
        if not path.is_dir() and not path.is_file():
            return "unavailable"
        return "observed"
    except OSError:
        return "unavailable"


def _relationship_map(path: Path) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}

    for observation in collect_relationships(path):
        if not observation.target:
            continue
        result.setdefault(observation.entry, []).append(observation.target)

    return {
        key: sorted(set(values))
        for key, values in sorted(result.items())
    }


def collect_bus_objects(limit: int = 4096) -> dict[str, Any]:
    """Collect bounded generic sysfs bus objects and direct relationships."""
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise TypeError("limit must be an integer")
    if limit < 1 or limit > 100000:
        raise ValueError("limit must be between 1 and 100000")

    objects: list[dict[str, Any]] = []
    seen = 0
    truncated = False

    try:
        buses = sorted(SYSFS_BUS.iterdir(), key=lambda item: item.name)
    except (FileNotFoundError, PermissionError, OSError):
        buses = []

    for bus in buses:
        devices = bus / "devices"
        if not devices.is_dir():
            continue

        try:
            entries = sorted(devices.iterdir(), key=lambda item: item.name)
        except (FileNotFoundError, PermissionError, OSError):
            continue

        for entry in entries:
            seen += 1
            if len(objects) >= limit:
                truncated = True
                continue

            try:
                resolved = str(entry.resolve())
            except (FileNotFoundError, OSError):
                resolved = ""

            relationships = _relationship_map(entry)
            driver_targets = relationships.get("driver", [])
            module_targets: list[str] = []

            for driver_target in driver_targets:
                module_targets.extend(
                    _relationship_map(Path(driver_target)).get("module", [])
                )

            objects.append(
                {
                    "bus": bus.name,
                    "name": entry.name,
                    "path": str(entry),
                    "resolved_path": resolved,
                    "driver": (
                        Path(driver_targets[0]).name
                        if driver_targets
                        else None
                    ),
                    "module": (
                        Path(module_targets[0]).name
                        if module_targets
                        else None
                    ),
                    "relationships": relationships,
                }
            )

    return {
        "status": _source_status(SYSFS_BUS),
        "objects": objects,
        "returned": len(objects),
        "observed": seen,
        "limit": limit,
        "truncated": truncated,
    }


def collect_inventory(sysfs_limit: int = 4096) -> dict[str, Any]:
    """Return one JSON-serializable, evidence-oriented hardware snapshot."""
    audio = collect_audio()
    usb = collect_usb()
    sysfs = collect_bus_objects(limit=sysfs_limit)

    return {
        "schema": "linux-hardware-enumerator",
        "schema_version": SCHEMA_VERSION,
        "collected_at": datetime.now(timezone.utc).isoformat(),
        "host": {
            "hostname": socket.gethostname(),
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
        },
        "sources": {
            "alsa_cards": _source_status(Path("/proc/asound/cards")),
            "alsa_pcm": _source_status(Path("/proc/asound/pcm")),
            "asoc_components": _source_status(
                Path("/sys/kernel/debug/asoc/components")
            ),
            "asoc_dais": _source_status(Path("/sys/kernel/debug/asoc/dais")),
            "usb_sysfs": _source_status(Path("/sys/bus/usb/devices")),
            "sysfs_bus": sysfs["status"],
        },
        "audio": asdict(audio),
        "usb": asdict(usb),
        "sysfs": sysfs,
    }


__all__ = [
    "SCHEMA_VERSION",
    "collect_bus_objects",
    "collect_inventory",
]
