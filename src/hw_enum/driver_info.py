from dataclasses import dataclass
from pathlib import Path

from hw_enum.relationships import collect_relationships


@dataclass
class DriverInfo:
    object_path: str
    driver_path: str
    driver_name: str
    module_path: str
    module_name: str


def _name_from_path(path: str) -> str:
    if not path:
        return ""

    return Path(path).name


def collect_driver_info(path: str | Path) -> DriverInfo:
    object_path = Path(path)
    relationships = collect_relationships(object_path)

    driver_path = ""
    module_path = ""

    for relationship in relationships:
        if relationship.relation == "driver":
            driver_path = relationship.target

    if driver_path:
        driver_relationships = collect_relationships(Path(driver_path))

        for relationship in driver_relationships:
            if relationship.relation == "module":
                module_path = relationship.target

    return DriverInfo(
        object_path=str(object_path),
        driver_path=driver_path,
        driver_name=_name_from_path(driver_path),
        module_path=module_path,
        module_name=_name_from_path(module_path),
    )


def enumerate_driver_info(path: str | Path) -> None:
    info = collect_driver_info(path)

    print(f"=== DRIVER INFORMATION: {info.object_path} ===")
    print(f"Driver path: {info.driver_path or '(none or unavailable)'}")
    print(f"Driver name: {info.driver_name or '(unknown)'}")
    print(f"Module path: {info.module_path or '(none or unavailable)'}")
    print(f"Module name: {info.module_name or '(unknown)'}")


if __name__ == "__main__":
    enumerate_driver_info("/sys/bus/usb/devices/3-2:1.0")