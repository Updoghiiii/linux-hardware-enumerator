from dataclasses import dataclass, field
from pathlib import Path
import re


@dataclass
class AudioPCM:
    device: int
    name: str
    playback: bool
    capture: bool


@dataclass
class AudioCard:
    index: int
    identifier: str
    driver: str
    name: str
    pcm: list[AudioPCM] = field(default_factory=list)


@dataclass
class AudioInventory:
    alsa_cards: list[AudioCard]
    asoc_components: str
    asoc_dais: str


def _read(path: str) -> str:
    try:
        return Path(path).read_text().strip()
    except (FileNotFoundError, PermissionError, OSError):
        return ""


def _parse_alsa_cards(text: str) -> list[AudioCard]:
    cards = []

    for match in re.finditer(
        r"^\s*(\d+)\s+\[([^\]]+)\]:\s+(\S+)\s+-\s+(.+)$",
        text,
        re.MULTILINE,
    ):
        cards.append(
            AudioCard(
                index=int(match.group(1)),
                identifier=match.group(2).strip(),
                driver=match.group(3),
                name=match.group(4).strip(),
            )
        )

    return cards


def _parse_alsa_pcm(text: str) -> list[tuple[int, AudioPCM]]:
    devices = []

    for line in text.splitlines():
        match = re.match(
            r"^(\d+)-(\d+):\s+(.+?)\s+:\s+(.+?)\s+:\s*(.*)$",
            line,
        )

        if not match:
            continue

        capabilities = match.group(5)

        devices.append(
            (
                int(match.group(1)),
                AudioPCM(
                    device=int(match.group(2)),
                    name=match.group(3).strip(),
                    playback="playback" in capabilities,
                    capture="capture" in capabilities,
                ),
            )
        )

    return devices


def collect_audio() -> AudioInventory:
    cards = _parse_alsa_cards(_read("/proc/asound/cards"))

    for card_index, pcm in _parse_alsa_pcm(_read("/proc/asound/pcm")):
        for card in cards:
            if card.index == card_index:
                card.pcm.append(pcm)
                break

    return AudioInventory(
        alsa_cards=cards,
        asoc_components=_read("/sys/kernel/debug/asoc/components"),
        asoc_dais=_read("/sys/kernel/debug/asoc/dais"),
    )


def enumerate_audio() -> None:
    inventory = collect_audio()

    print("=== ALSA CARDS ===")

    if inventory.alsa_cards:
        for card in inventory.alsa_cards:
            print(f"Card {card.index}:")
            print(f"  Identifier: {card.identifier}")
            print(f"  Driver:     {card.driver}")
            print(f"  Name:       {card.name}")

            if card.pcm:
                print("  PCM devices:")

                for pcm in card.pcm:
                    directions = []

                    if pcm.playback:
                        directions.append("playback")

                    if pcm.capture:
                        directions.append("capture")

                    print(f"    Device {pcm.device}:")
                    print(f"      Name:       {pcm.name}")
                    print(
                        f"      Directions: {', '.join(directions) or 'none'}"
                    )
            else:
                print("  PCM devices: (none)")

    else:
        print("(none)")

    print("\n=== ASoC COMPONENTS ===")
    print(inventory.asoc_components or "(none or unavailable)")

    print("\n=== ASoC DAIs ===")
    print(inventory.asoc_dais or "(none or unavailable)")


if __name__ == "__main__":
    enumerate_audio()
