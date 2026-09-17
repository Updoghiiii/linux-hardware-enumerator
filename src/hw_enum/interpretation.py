from dataclasses import dataclass

from hw_enum.relationships import SysfsObservation


@dataclass
class SysfsInterpretation:
    source: str
    entry: str
    kind: str
    target: str = ""
    meaning: str = "unknown"
    confidence: str = "unknown"


RELATIONSHIP_MEANINGS = {
    "driver": "driver_reference",
    "subsystem": "subsystem_reference",
    "device": "device_reference",
    "port": "port_reference",
    "peer": "peer_reference",
    "firmware_node": "firmware_reference",
    "physical_node": "physical_reference",
}


def interpret_observation(
    observation: SysfsObservation,
) -> SysfsInterpretation:
    meaning = "unknown"
    confidence = "unknown"

    if (
        observation.kind == "symlink"
        and observation.entry in RELATIONSHIP_MEANINGS
    ):
        meaning = RELATIONSHIP_MEANINGS[observation.entry]
        confidence = "observed"

    return SysfsInterpretation(
        source=observation.source,
        entry=observation.entry,
        kind=observation.kind,
        target=observation.target,
        meaning=meaning,
        confidence=confidence,
    )
