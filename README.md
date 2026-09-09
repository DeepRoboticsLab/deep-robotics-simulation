# DEEPRobotics Simulation

**English** | [简体中文](README_CN.md)

DEEPRobotics Simulation is a MuJoCo-based simulation repository for DEEPRobotics products.

Each product keeps its runtime configuration, scene composition, Topics, and
control behavior in its own directory. This README documents only the shared
environment, repository layout, and product navigation.

## 1. Products

| Product | Start Command | Documentation |
| --- | --- | --- |
| DR02 Pro | `python3 run_sim.py dr02_pro` | [English](dr02_pro/README.md) / [中文](dr02_pro/README_CN.md) |
| DR02 Std | `python3 run_sim.py dr02_std` | [English](dr02_std/README.md) / [中文](dr02_std/README_CN.md) |

## 2. Supported Environments

The following environment combinations are supported:

| Ubuntu | ROS 2 | Python |
| --- | --- | --- |
| 22.04 | Humble | 3.10 |
| 24.04 | Jazzy | 3.12 |

## 3. Environment Setup

Install ROS 2 and the `drdds` message interface package before configuring the
Python environment. `drdds` is provided by the
[deep-robotics-msg](https://github.com/DeepRoboticsLab/deep-robotics-msg.git)
repository. Use the installer below, or follow the linked repository documentation
for manual installation and source builds.

### 3.1 Install the Message Interfaces

The script checks dependencies, downloads the message source, and builds and
installs its Debian package. Missing dependencies are reported, never installed.
ROS 2, a compiler, CMake/CPack, colcon, and the required ROS message-generation
packages must already be present. Run from this repository root:

```bash
./scripts/install_deep_robotics_msg.sh
```

If the source has already been downloaded or transferred, use it directly:

```bash
./scripts/install_deep_robotics_msg.sh --source-dir ~/deep-robotics-msg
```

`--source-dir` skips downloading and requires no internet connection. The script
never runs apt. It builds a temporary copy, preserves supplied sources, and cleans
up temporary files. Sudo is used only to install the built package.

Ubuntu 22.04 selects Humble; Ubuntu 24.04 selects Jazzy. Both amd64 and arm64 are
supported for message builds. Optional: `--ref <tag-or-commit>` selects the downloaded
revision (default: `main`); `--jobs N` sets compiler parallelism (default: 2).
`--ref` cannot be combined with `--source-dir`. See `--help` for usage.

If matching interfaces were already installed on this host using the SDK installer,
skip this step. After Debian installation, source `/opt/ros/<ros-distro>/setup.bash`
in each terminal (`humble` on Ubuntu 22.04, `jazzy` on Ubuntu 24.04). If using a
source workspace instead, also source its `install/setup.bash` before activating
the Python environment.

### 3.2 First-Time Setup

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

## 4. Run

After the first-time setup, run the following commands from the repository root
in each new terminal:

```bash
source /opt/ros/<ros-distro>/setup.bash
source .venv/bin/activate
python3 run_sim.py <product>
```

## 5. Using with the SDK

The simulator and
[deep-robotics-sdk2](https://github.com/DeepRoboticsLab/deep-robotics-sdk2) run as
separate processes. Start the simulation for the selected product in one
terminal, then follow the SDK product documentation to run a supported program
in another terminal.

Both terminals must use the same ROS 2 distribution and `drdds` message
interface version. If `ROS_DOMAIN_ID` is configured, use the same value in both
terminals. See the corresponding product documentation for supported SDK
features and configuration.

## 6. Repository Layout

```text
scripts/         Dependency installation helpers
run_sim.py       Product simulation entry point
simulator.py     Shared MuJoCo lifecycle, timing, viewer, and cleanup
sim_config.py    Shared YAML loading and runtime configuration validation
worlds/basic/    Shared skybox, lighting, and collidable ground
worlds/demo/     Built-in demonstration terrain and environment assets
<product>/       Product-specific simulation, model, scene, and documentation
```

## 7. Related Repositories

- [deep-robotics-sdk2](https://github.com/DeepRoboticsLab/deep-robotics-sdk2): ROS 2 SDK, state machines, and Topic examples for DEEPRobotics products.
- [deep-robotics-msg](https://github.com/DeepRoboticsLab/deep-robotics-msg.git): ROS 2 message interface package shared by the Simulation and SDK. Its ROS 2 package name is `drdds`.
