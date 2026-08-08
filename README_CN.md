# DEEPRobotics Simulation

[English](README.md) | **简体中文**

DEEPRobotics Simulation 是面向 DEEPRobotics 产品的 MuJoCo 仿真仓库。

每个产品目录独立维护运行配置、场景组合、Topic 和控制行为。本 README 仅说明公共环境、仓库结构和产品导航。

## 产品列表

| 产品 | 启动命令 | 产品文档 |
| --- | --- | --- |
| DR02 Pro | `python3 run_sim.py dr02_pro` | [English](dr02_pro/README.md) / [中文](dr02_pro/README_CN.md) |
| DR02 Std | `python3 run_sim.py dr02_std` | [English](dr02_std/README.md) / [中文](dr02_std/README_CN.md) |

## 支持环境

当前支持以下环境组合：

| Ubuntu | ROS 2 | Python |
| --- | --- | --- |
| 22.04 | Humble | 3.10 |
| 24.04 | Jazzy | 3.12 |

## 环境配置

配置 Python 环境前，应先安装 ROS 2 和 `drdds` 消息接口库。`drdds` 由 [deep-robotics-msg](https://github.com/DeepRoboticsLab/deep-robotics-msg) 仓库提供，安装和环境加载方式以该仓库的 README 为准。

### 首次配置

首次配置仓库时，在仓库根目录执行：

```bash
sudo apt install python3-venv
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

`python3-venv` 在同一系统中只需安装一次；`.venv` 创建完成后，后续运行不需要重新创建或安装依赖。

## 运行

首次配置完成后，每次打开新终端，在仓库根目录执行：

```bash
source /opt/ros/<ros-distro>/setup.bash
source .venv/bin/activate
python3 run_sim.py <product>
```

## 与 SDK 配合使用

仿真程序和 [deep-robotics-sdk2](https://github.com/DeepRoboticsLab/deep-robotics-sdk2) 是两个独立进程。使用时，应先在一个终端启动对应产品的仿真程序，再在另一个终端按照 SDK 产品文档运行支持仿真的程序。

两个终端应使用相同的 ROS 2 发行版和 `drdds` 消息接口版本；如配置了 `ROS_DOMAIN_ID`，两端应使用相同的值。各产品支持的 SDK 功能和配置方式请参阅对应产品文档。

## 仓库结构

```text
run_sim.py       产品仿真启动入口
simulator.py     公共 MuJoCo 生命周期、时间推进、Viewer 与资源关闭
sim_config.py    公共 YAML 加载与运行配置校验
worlds/basic/    公共天空、灯光和可碰撞地面
worlds/demo/     仓库自带演示地形和环境资源
<product>/       产品专属仿真、模型、场景和文档
```

## 相关仓库

- [deep-robotics-sdk2](https://github.com/DeepRoboticsLab/deep-robotics-sdk2)：DEEPRobotics 产品的 ROS 2 SDK、状态机和 Topic 示例。
- [deep-robotics-msg](https://github.com/DeepRoboticsLab/deep-robotics-msg)：Simulation 与 SDK 共用的 ROS 2 消息接口库，ROS 2 包名为 `drdds`。
