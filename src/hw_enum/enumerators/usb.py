from dataclasses import dataclass, field
from pathlib import Path


USB_SYSFS = Path("/sys/bus/usb/devices")


@dataclass
class USBInterface:
    sysfs_name: str
    number: int
    interface_class: str
    subclass: str
    protocol: str
    num_endpoints: int
    driver: str


@dataclass
class USBDevice:
    sysfs_name: str
    bus_number: int
    device_number: int
    parent: str
    vendor_id: str
    product_id: str
    manufacturer: str
    product: str
    serial: str
    speed: str
    driver: str
    interfaces: list[USBInterface] = field(default_factory=list)


@dataclass
class USBInventory:
    devices: list[USBDevice]


def _read(path: Path) -> str:
    try:
        return path.read_text().strip()
    except (FileNotFoundError, PermissionError, OSError):
        return ""


def _read_int(path: Path, default: int = 0) -> int:
    value = _read(path)

    try:
        return int(value)
    except ValueError:
        return default


def _driver_name(path: Path) -> str:
    try:
        return path.resolve().name
    except (FileNotFoundError, OSError):
        return ""


def _is_usb_device(path: Path) -> bool:
    return ":" not in path.name and "-" in path.name


def _parse_device_name(name: str) -> tuple[int, int]:
    bus, device = name.split("-", 1)
    return int(bus), int(device.split(".", 1)[0])


def _parse_interface(path: Path) -> USBInterface:
    return USBInterface(
        sysfs_name=path.name,
        number=_read_int(path / "bInterfaceNumber"),
        interface_class=_read(path / "bInterfaceClass"),
        subclass=_read(path / "bInterfaceSubClass"),
        protocol=_read(path / "bInterfaceProtocol"),
        num_endpoints=_read_int(path / "bNumEndpoints"),
        driver=_driver_name(path / "driver"),
    )


def _find_interfaces(device_path: Path) -> list[USBInterface]:
    interfaces = []

    try:
        paths = sorted(USB_SYSFS.iterdir())
    except (FileNotFoundError, PermissionError, OSError):
        return interfaces

    for path in paths:
        if not path.is_dir():
            continue

        if not path.name.startswith(f"{device_path.name}:"):
            continue

        interfaces.append(_parse_interface(path))

    return interfaces


def _parent_name(device_path: Path) -> str:
    name = device_path.name

    if "." not in name:
        return name.split("-", 1)[0]

    return name.rsplit(".", 1)[0]


def _parse_device(path: Path) -> USBDevice:
    bus_number, device_number = _parse_device_name(path.name)

    return USBDevice(
        sysfs_name=path.name,
        bus_number=bus_number,
        device_number=device_number,
        parent=_parent_name(path),
        vendor_id=_read(path / "idVendor"),
        product_id=_read(path / "idProduct"),
        manufacturer=_read(path / "manufacturer"),
        product=_read(path / "product"),
        serial=_read(path / "serial"),
        speed=_read(path / "speed"),
        driver=_driver_name(path / "driver"),
        interfaces=_find_interfaces(path),
    )


def collect_usb() -> USBInventory:
    devices = []

    try:
        paths = sorted(USB_SYSFS.iterdir())
    except (FileNotFoundError, PermissionError, OSError):
        return USBInventory(devices=[])

    for path in paths:
        if not path.is_dir():
            continue

        if not _is_usb_device(path):
            continue

        try:
            devices.append(_parse_device(path))
        except (ValueError, OSError):
            continue

    return USBInventory(devices=devices)


def enumerate_usb() -> None:
    inventory = collect_usb()

    print("=== USB DEVICES ===")

    if not inventory.devices:
        print("(none or unavailable)")
        return

    for device in inventory.devices:
        print(f"Device {device.sysfs_name}:")
        print(f"  Bus:          {device.bus_number}")
        print(f"  Device:       {device.device_number}")
        print(f"  Parent:       {device.parent}")
        print(f"  Vendor ID:    {device.vendor_id or '(unknown)'}")
        print(f"  Product ID:   {device.product_id or '(unknown)'}")
        print(f"  Manufacturer: {device.manufacturer or '(unknown)'}")
        print(f"  Product:      {device.product or '(unknown)'}")
        print(f"  Serial:       {device.serial or '(unknown)'}")
        print(f"  Speed:        {device.speed or '(unknown)'}")
        print(f"  Driver:       {device.driver or '(none)'}")

        if device.interfaces:
            print("  Interfaces:")

            for interface in device.interfaces:
                print(f"    {interface.sysfs_name}:")
                print(f"      Number:      {interface.number}")
                print(f"      Class:       {interface.interface_class or '(unknown)'}")
                print(f"      Subclass:    {interface.subclass or '(unknown)'}")
                print(f"      Protocol:    {interface.protocol or '(unknown)'}")
                print(f"      Endpoints:   {interface.num_endpoints}")
                print(f"      Driver:      {interface.driver or '(none)'}")
        else:
            print("  Interfaces: (none)")


if __name__ == "__main__":
    enumerate_usb()