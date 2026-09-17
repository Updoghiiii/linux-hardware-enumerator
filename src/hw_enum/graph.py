from dataclasses import dataclass, field

from hw_enum.interpretation import SysfsInterpretation


@dataclass
class SysfsRelationship:
    source: str
    relationship: str
    target: str


@dataclass
class SysfsGraph:
    relationships: list[SysfsRelationship] = field(default_factory=list)


def relationship_from_interpretation(
    interpretation: SysfsInterpretation,
) -> SysfsRelationship | None:
    if interpretation.meaning == "unknown":
        return None

    if not interpretation.target:
        return None

    return SysfsRelationship(
        source=interpretation.source,
        relationship=interpretation.meaning,
        target=interpretation.target,
    )


def build_graph(
    interpretations: list[SysfsInterpretation],
) -> SysfsGraph:
    relationships = []

    for interpretation in interpretations:
        relationship = relationship_from_interpretation(
            interpretation
        )

        if relationship is not None:
            relationships.append(relationship)

    return SysfsGraph(relationships=relationships)


def enumerate_graph(graph: SysfsGraph) -> None:
    print("=== SYSFS RELATIONSHIP GRAPH ===")

    if not graph.relationships:
        print("(none)")
        return

    for relationship in graph.relationships:
        print(
            f"{relationship.source} "
            f"--{relationship.relationship}--> "
            f"{relationship.target}"
        )


if __name__ == "__main__":
    print("Sysfs graph module")
