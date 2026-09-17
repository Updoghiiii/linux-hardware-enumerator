from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SysfsRelationship:
    source: str
    relation: str
    target: str


@dataclass
class SysfsObject:
    path: str
    name: str
    relationships: list[SysfsRelationship] = field(default_factory=list)


def _relationship_target(path: Path) -> str:
    try:
        return str(path.resolve())
    except (FileNotFoundError, OSError):
        return ""


def collect_relationships(path: Path) -> list[SysfsRelationship]:
    relationships = []

    try:
        entries = sorted(path.iterdir())
    except (FileNotFoundError, PermissionError, OSError):
        return relationships

    for entry in entries:
        if not entry.is_symlink():
            continue

        target = _relationship_target(entry)

        if not target:
            continue

        relationships.append(
            SysfsRelationship(
                source=str(path),
                relation=entry.name,
                target=target,
            )
        )

    return relationships


def collect_sysfs_object(path: str | Path) -> SysfsObject:
    object_path = Path(path)

    return SysfsObject(
        path=str(object_path),
        name=object_path.name,
        relationships=collect_relationships(object_path),
    )


def walk_relationships(
    path: str | Path,
    max_depth: int = 3,
) -> list[SysfsRelationship]:
    relationships = []
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

        current_relationships = collect_relationships(current)
        relationships.extend(current_relationships)

        for relationship in current_relationships:
            target = Path(relationship.target)

            if target.is_dir():
                walk(target, depth + 1)

    walk(Path(path), 0)

    return relationships


def enumerate_relationships(path: str | Path) -> None:
    obj = collect_sysfs_object(path)

    print(f"=== SYSFS OBJECT: {obj.name} ===")
    print(f"Path: {obj.path}")

    if not obj.relationships:
        print("Relationships: (none or unavailable)")
        return

    print("Relationships:")

    for relationship in obj.relationships:
        print(f"  {relationship.relation} -> {relationship.target}")


def enumerate_relationship_tree(
    path: str | Path,
    max_depth: int = 3,
) -> None:
    relationships = walk_relationships(path, max_depth=max_depth)

    print(f"=== SYSFS RELATIONSHIP WALK: {path} ===")

    if not relationships:
        print("(none or unavailable)")
        return

    for relationship in relationships:
        print(
            f"{relationship.source} "
            f"--{relationship.relation}--> "
            f"{relationship.target}"
        )


if __name__ == "__main__":
    enumerate_relationship_tree("/sys/bus/usb/devices/3-2:1.0")