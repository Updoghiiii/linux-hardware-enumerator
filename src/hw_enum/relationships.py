from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SysfsObservation:
    source: str
    entry: str
    kind: str
    target: str = ""


@dataclass
class SysfsObject:
    path: str
    name: str
    observations: list[SysfsObservation] = field(default_factory=list)


def _resolve(path: Path) -> str:
    try:
        return str(path.resolve())
    except (FileNotFoundError, OSError):
        return ""


def _entry_kind(path: Path) -> str:
    if path.is_symlink():
        return "symlink"

    if path.is_dir():
        return "directory"

    if path.is_file():
        return "file"

    return "other"


def collect_observations(path: Path) -> list[SysfsObservation]:
    observations = []

    try:
        entries = sorted(path.iterdir())
    except (FileNotFoundError, PermissionError, OSError):
        return observations

    for entry in entries:
        kind = _entry_kind(entry)

        if kind == "symlink":
            observations.append(
                SysfsObservation(
                    source=str(path),
                    entry=entry.name,
                    kind=kind,
                    target=_resolve(entry),
                )
            )
            continue

        observations.append(
            SysfsObservation(
                source=str(path),
                entry=entry.name,
                kind=kind,
            )
        )

    return observations


def collect_sysfs_object(path: str | Path) -> SysfsObject:
    object_path = Path(path)

    return SysfsObject(
        path=str(object_path),
        name=object_path.name,
        observations=collect_observations(object_path),
    )


def _child_directories(
    path: Path,
    observations: list[SysfsObservation],
) -> list[Path]:
    children = []

    for observation in observations:
        if observation.kind != "directory":
            continue

        children.append(path / observation.entry)

    return children


def walk_observations(
    path: str | Path,
    max_depth: int = 3,
) -> list[SysfsObservation]:
    observations = []
    visited = set()

    def walk(current: Path, depth: int) -> None:
        if depth > max_depth:
            return

        try:
            resolved = current.resolve()
        except (FileNotFoundError, OSError):
            return

        if resolved in visited:
            return

        visited.add(resolved)

        current_observations = collect_observations(current)
        observations.extend(current_observations)

        for child in _child_directories(
            current,
            current_observations,
        ):
            walk(child, depth + 1)

    walk(Path(path), 0)

    return observations


def enumerate_relationships(path: str | Path) -> None:
    obj = collect_sysfs_object(path)

    print(f"=== SYSFS OBJECT: {obj.name} ===")
    print(f"Path: {obj.path}")

    if not obj.observations:
        print("Observations: (none or unavailable)")
        return

    print("Observations:")

    for observation in obj.observations:
        if observation.kind == "symlink":
            print(
                f"  {observation.entry} "
                f"[symlink] -> {observation.target or '(unresolved)'}"
            )
        else:
            print(
                f"  {observation.entry} "
                f"[{observation.kind}]"
            )


def enumerate_relationship_tree(
    path: str | Path,
    max_depth: int = 3,
) -> None:
    observations = walk_observations(
        path,
        max_depth=max_depth,
    )

    print(f"=== SYSFS OBSERVATION WALK: {path} ===")

    if not observations:
        print("(none or unavailable)")
        return

    for observation in observations:
        if observation.kind == "symlink":
            print(
                f"{observation.source} "
                f"--{observation.entry}--> "
                f"{observation.target or '(unresolved)'}"
            )
        else:
            print(
                f"{observation.source} "
                f"--contains {observation.entry} "
                f"[{observation.kind}]"
            )


if __name__ == "__main__":
    enumerate_relationship_tree("/sys/bus/usb/devices/3-2")
