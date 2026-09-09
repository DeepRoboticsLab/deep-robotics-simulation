# DEEPRobotics Simulation

**English** | [简体中文](README_CN.md)

DEEPRobotics Simulation is a MuJoCo-based simulation repository for DEEPRobotics products.

Each product keeps its runtime configuration, scene composition, Topics, and
control behavior in its own directory. This README documents only the shared
environment, repository layout, and product navigation.

## Products

| Product | Start Command | Documentation |
| --- | --- | --- |
| DR02 Pro | `python3 run_sim.py dr02_pro` | [English](dr02_pro/README.md) / [中文](dr02_pro/README_CN.md) |
| DR02 Std | `python3 run_sim.py dr02_std` | [English](dr02_std/README.md) / [中文](dr02_std/README_CN.md) |

## Supported Environments

The following environment combinations are supported:

| Ubuntu | ROS 2 | Python |
| --- | --- | --- |
| 22.04 | Humble | 3.10 |
| 24.04 | Jazzy | 3.12 |

## Environment Setup

Install ROS 2 and the `drdds` message interface package before configuring the
Python environment. `drdds` is provided by the
[deep-robotics-msg](https://github.com/DeepRoboticsLab/deep-robotics-msg.git)
repository. Use the installer below, or follow the linked repository documentation
for manual installation and source builds.

### Install the Message Interfaces

Install ROS 2 and configure its apt repository first, then run from this repository root:

```bash
./scripts/install_deep_robotics_msg.sh
```

The script selects Humble on Ubuntu 22.04 or Jazzy on Ubuntu 24.04 and supports
native x86-64 (`amd64`) and 64-bit ARM (`arm64`) builds of the message interfaces.
It installs build dependencies with apt, downloads the source, builds and installs
the Debian package into `/opt/ros/<distro>`, and verifies the `drdds` interfaces.
System installation uses sudo. Temporary downloads and build files are removed on
success or failure; shell startup files are not edited. ROS 2 itself is not installed.

The default source is upstream `main`. Use `--ref <tag-or-full-commit-SHA>` to select
a repeatable version and `--jobs N` to adjust compiler parallelism (default: 2).
See `--help` for all options. Running the script again rebuilds and reinstalls the
selected revision. If the matching interfaces were already installed on this host
using the SDK installer, skip this step.

After Debian installation, sourcing `/opt/ros/<ros-distro>/setup.bash` is sufficient;
use `humble` on Ubuntu 22.04 or `jazzy` on Ubuntu 24.04. If you build the messages
as a source workspace instead, also source that workspace's `install/setup.bash`
in each terminal before activating the Python environment.

### First-Time Setup

Run the following commands once from the repository root:

```bash
sudo apt install python3-venv
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

`python3-venv` only needs to be installed once on a system. After `.venv` has
been created, it does not need to be recreated and the dependencies do not need
to be reinstalled on subsequent runs.

## Run

After the first-time setup, run the following commands from the repository root
in each new terminal:

```bash
source /opt/ros/<ros-distro>/setup.bash
source .venv/bin/activate
python3 run_sim.py <product>
```

## Using with the SDK

The simulator and
[deep-robotics-sdk2](https://github.com/DeepRoboticsLab/deep-robotics-sdk2) run as
separate processes. Start the simulation for the selected product in one
terminal, then follow the SDK product documentation to run a supported program
in another terminal.

Both terminals must use the same ROS 2 distribution and `drdds` message
interface version. If `ROS_DOMAIN_ID` is configured, use the same value in both
terminals. See the corresponding product documentation for supported SDK
features and configuration.

## Repository Layout

```text
scripts/         Dependency installation helpers
run_sim.py       Product simulation entry point
simulator.py     Shared MuJoCo lifecycle, timing, viewer, and cleanup
sim_config.py    Shared YAML loading and runtime configuration validation
worlds/basic/    Shared skybox, lighting, and collidable ground
worlds/demo/     Built-in demonstration terrain and environment assets
<product>/       Product-specific simulation, model, scene, and documentation
```

## Related Repositories

- [deep-robotics-sdk2](https://github.com/DeepRoboticsLab/deep-robotics-sdk2): ROS 2 SDK, state machines, and Topic examples for DEEPRobotics products.
- [deep-robotics-msg](https://github.com/DeepRoboticsLab/deep-robotics-msg.git): ROS 2 message interface package shared by the Simulation and SDK. Its ROS 2 package name is `drdds`.
