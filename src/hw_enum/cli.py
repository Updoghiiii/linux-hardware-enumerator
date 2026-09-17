from pathlib import Path

from hw_enum.enumerators.audio import enumerate_audio
from hw_enum.relationships import walk_observations
from hw_enum.interpretation import interpret_observation
from hw_enum.graph import build_graph, enumerate_graph


def enumerate_sysfs() -> None:
    target = Path("/sys/bus/usb/devices/3-2")

    print("\n=== GENERIC SYSFS DISCOVERY ===")

    if not target.exists():
        print(f"Target unavailable: {target}")
        return

    observations = walk_observations(
        target,
        max_depth=5,
    )

    interpretations = [
        interpret_observation(observation)
        for observation in observations
    ]

    graph = build_graph(interpretations)

    enumerate_graph(graph)


def main():
    print("Linux Hardware Enumerator")
    print("==========================")

    enumerate_audio()
    enumerate_sysfs()


if __name__ == "__main__":
    main()
