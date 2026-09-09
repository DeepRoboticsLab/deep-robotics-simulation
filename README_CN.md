# DEEPRobotics Simulation

[English](README.md) | **简体中文**

DEEPRobotics Simulation 是面向 DEEPRobotics 产品的 MuJoCo 仿真仓库。

每个产品目录独立维护运行配置、场景组合、Topic 和控制行为。本 README 仅说明公共环境、仓库结构和产品导航。

## 1. 产品列表

| 产品 | 启动命令 | 产品文档 |
| --- | --- | --- |
| DR02 Pro | `python3 run_sim.py dr02_pro` | [English](dr02_pro/README.md) / [中文](dr02_pro/README_CN.md) |
| DR02 Std | `python3 run_sim.py dr02_std` | [English](dr02_std/README.md) / [中文](dr02_std/README_CN.md) |

## 2. 支持环境

当前支持以下环境组合：

| Ubuntu | ROS 2 | Python |
| --- | --- | --- |
| 22.04 | Humble | 3.10 |
| 24.04 | Jazzy | 3.12 |

## 3. 环境配置

配置 Python 环境前，应先安装 ROS 2 和 `drdds` 消息接口库。`drdds` 由 [deep-robotics-msg](https://github.com/DeepRoboticsLab/deep-robotics-msg.git) 仓库提供，可使用下方脚本自动安装；手动安装或源码编译步骤请参阅该仓库文档。

### 3.1 安装消息接口

脚本检查依赖，下载消息源码，然后编译并安装其 deb 包。缺少依赖时仅报错，
不会安装依赖。目标主机需已具备 ROS 2、编译器、CMake/CPack、colcon 和所需
ROS 消息生成包。在本仓库根目录执行：

```bash
./scripts/install_deep_robotics_msg.sh
```

如果源码已下载或传入本机，直接使用：

```bash
./scripts/install_deep_robotics_msg.sh --source-dir ~/deep-robotics-msg
```

`--source-dir` 跳过下载，无需联网。脚本不执行 apt，只创建源码临时副本进行
编译，保留原始源码并清理临时文件。仅安装生成的 deb 包时使用 sudo。

Ubuntu 22.04 自动选择 Humble，Ubuntu 24.04 自动选择 Jazzy，消息编译支持
amd64 和 arm64。可选参数：`--ref <标签或提交>` 指定下载版本（默认 `main`），
`--jobs N` 设置编译并行数（默认 2）。`--ref` 不可与 `--source-dir` 同时使用，
完整用法见 `--help`。

如果本机已通过 SDK 安装脚本安装了相同版本的消息接口，可跳过此步骤。
通过 deb 安装后，每个终端加载 `/opt/ros/<ros-distro>/setup.bash` 即可：
Ubuntu 22.04 使用 `humble`，Ubuntu 24.04 使用 `jazzy`。如果选择源码工作空间
方式，还需在激活 Python 环境前加载消息工作空间的 `install/setup.bash`。

### 3.2 首次配置

首次配置仓库时，在仓库根目录执行：

```bash
sudo apt install python3-venv
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

`python3-venv` 在同一系统中只需安装一次；`.venv` 创建完成后，后续运行不需要重新创建或安装依赖。

## 4. 运行

首次配置完成后，每次打开新终端，在仓库根目录执行：

```bash
source /opt/ros/<ros-distro>/setup.bash
source .venv/bin/activate
python3 run_sim.py <product>
```

## 5. 与 SDK 配合使用

仿真程序和 [deep-robotics-sdk2](https://github.com/DeepRoboticsLab/deep-robotics-sdk2) 是两个独立进程。使用时，应先在一个终端启动对应产品的仿真程序，再在另一个终端按照 SDK 产品文档运行支持仿真的程序。

两个终端应使用相同的 ROS 2 发行版和 `drdds` 消息接口版本；如配置了 `ROS_DOMAIN_ID`，两端应使用相同的值。各产品支持的 SDK 功能和配置方式请参阅对应产品文档。

## 6. 仓库结构

```text
scripts/         依赖安装脚本
run_sim.py       产品仿真启动入口
simulator.py     公共 MuJoCo 生命周期、时间推进、Viewer 与资源关闭
sim_config.py    公共 YAML 加载与运行配置校验
worlds/basic/    公共天空、灯光和可碰撞地面
worlds/demo/     仓库自带演示地形和环境资源
<product>/       产品专属仿真、模型、场景和文档
```

## 7. 相关仓库

- [deep-robotics-sdk2](https://github.com/DeepRoboticsLab/deep-robotics-sdk2)：DEEPRobotics 产品的 ROS 2 SDK、状态机和 Topic 示例。
- [deep-robotics-msg](https://github.com/DeepRoboticsLab/deep-robotics-msg.git)：Simulation 与 SDK 共用的 ROS 2 消息接口库，ROS 2 包名为 `drdds`。
