# Linux Hardware Enumerator

A Linux hardware discovery and learning tool.

The goal is not to provide a collection of machine-specific shell commands.
The goal is to build a program that interrogates Linux itself, discovers what
the kernel exposes about the machine, correlates those observations, and
builds a structured hardware inventory.

The program should work across different Linux distributions, kernels,
drivers, architectures, and hardware platforms without assuming that every
machine exposes hardware through the same interfaces.

## Core idea

Linux hardware can be represented through many different kernel and userspace
interfaces.

Examples include:

- `/proc`
- `/sys`
- debugfs
- device tree
- ALSA
- ASoC
- PCI
- USB
- I2C
- SPI
- GPIO
- kernel driver information
- udev information
- platform devices
- kernel modules

No single interface should be treated as the definition of a piece of
hardware.

A filesystem path, driver name, device-tree node, or userspace interface is
evidence about the hardware.

The enumerator should collect that evidence and determine what can be
reasonably established from it.

## Learning-oriented design

The enumerator is intended to progressively build knowledge about Linux
hardware.

"Learning" does not mean modifying the program's source code automatically.
Instead, the program should accumulate structured observations and knowledge
about hardware encountered on different Linux systems.

For example, the program may encounter the same hardware class represented
differently by different kernels or platforms.

One system might expose information through ALSA and sysfs while another also
exposes ASoC, device-tree, or vendor-specific information.

The program should be able to record those differences rather than assuming
one representation is universal.

Over time, observations from different machines can be correlated to improve
the program's understanding of hardware, drivers, interfaces, and
relationships.

## Evidence before interpretation

The architecture should distinguish between:

- **Observed** - directly reported by Linux.
- **Interpreted** - meaning derived from observed information.
- **Known** - information supported by established knowledge.
- **Likely** - a useful interpretation that is not yet certain.
- **Unknown** - insufficient information to determine the answer.
- **Unavailable** - the information source could not be accessed.
- **Absent** - the relevant hardware or interface was actually determined
  not to be present.

Unavailable must never automatically mean absent.

For example, if debugfs is not mounted, the correct result is that the ASoC
debugfs information is unavailable. It must not be reported as proof that
ASoC hardware does not exist.

## Architecture

The project is intended to grow into four major layers.

### 1. Probes

Probes interrogate individual Linux information sources.

Examples:

- ALSA procfs
- sysfs
- ASoC debugfs
- device tree
- PCI
- USB
- I2C
- SPI
- GPIO
- kernel modules
- udev
- platform devices

A probe gathers evidence. It should avoid making assumptions about the
complete physical hardware model.

### 2. Normalized hardware model

Raw observations should eventually be represented as structured hardware
objects.

A hardware object may contain:

- identity
- type
- manufacturer
- driver
- kernel representation
- interfaces
- capabilities
- state
- relationships
- evidence
- confidence

The model should preserve relationships between components rather than
flattening everything into unrelated records.

For example:

```text
Audio system
└── ALSA card
    ├── PCM device
    ├── PCM device
    └── driver
```

### 3. Knowledge

The project should eventually maintain persistent knowledge about hardware
representations encountered on different Linux systems.

Knowledge may include relationships such as:

- driver to hardware
- device-tree compatible string to hardware class
- kernel representation to subsystem
- subsystem interface to physical component
- multiple Linux representations of the same hardware class

Knowledge should remain distinguishable from direct observations.

### 4. Output

The enumerator should eventually provide both:

- human-readable output for investigation
- machine-readable output for other software

JSON is the intended machine-readable format.

The machine-readable representation should make it possible for another
program to consume the hardware inventory without having to understand the
underlying Linux interfaces itself.

## Development strategy

Development begins with audio because it provides multiple layers of Linux
hardware representation:

- ALSA
- ASoC
- sysfs
- debugfs
- device tree
- kernel drivers

The first development machine is the Linux workstation, where the discovery
behavior can be developed and tested in a known environment.

The first embedded validation target is the BigTreeTech Pi V1.2.1 / CB1.

The same enumerator should be run on the CB1 without rewriting the discovery
logic specifically for that machine.

The CB1 is particularly useful because its embedded Linux audio stack exposes
ALSA and ASoC information that differs from the workstation's HDA-based
audio stack.

The goal is to use the enumerator itself to perform the hardware investigation
that would otherwise require manually inspecting kernel interfaces.

## Initial audio model

Audio currently begins with ALSA cards and their PCM devices.

Example:

```text
AudioInventory
└── ALSA Card
    ├── PCM device
    ├── PCM device
    └── ...
```

The model will expand as additional Linux audio evidence is incorporated.

## Long-term scope

After audio is established across multiple Linux systems, the enumerator can
expand into other hardware subsystems, including:

- PCI
- USB
- I2C
- SPI
- GPIO
- device tree
- platform devices
- kernel modules
- storage
- networking
- display
- sensors
- power management
- clocks
- regulators

The long-term objective is a general Linux hardware discovery system rather
than a collection of unrelated subsystem-specific scripts.
