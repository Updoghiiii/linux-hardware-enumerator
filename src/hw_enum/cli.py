from pathlib import Path

from hw_enum.enumerators.audio import enumerate_audio
from hw_enum.relationships import walk_observations
from hw_enum.interpretation import interpret_observation
from hw_enum.graph import build_graph, enumerate_graph


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


def main():
    print("Linux Hardware Enumerator")
    print("==========================")

    enumerate_audio()
    enumerate_sysfs()


if __name__ == "__main__":
    main()
