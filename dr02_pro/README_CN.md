# DR02 Pro 仿真

本文档说明 DR02 Pro 仿真。完成 [DEEPRobotics Simulation 根 README](../README_CN.md) 中的环境配置后，在仓库根目录运行：

```bash
python3 run_sim.py dr02_pro
```

## 配置

[`config.yaml`](config.yaml) 用于配置 DR02 Pro 仿真运行参数。

| 配置段 | 字段 | 说明 |
| --- | --- | --- |
| 根节点 | `scene` | 完整 MJCF 场景路径，相对于 `config.yaml`。 |
| `simulation` | `timestep_s` | MuJoCo 物理步长，单位为秒。 |
| `simulation` | `publish_frequency_hz` | `/JOINTS_DATA` 和 IMU Topic 发布频率，单位为 Hz。 |
| `simulation` | `command_timeout_s` | 命令超时时间，单位为秒。whole 模式输出 0 力矩并继续仿真；upper 模式暂停物理并保持实际姿态。 |
| `control` | `mode` | `default`、`whole` 或 `upper`。 |
| `viewer` | `enabled` | 是否启动 MuJoCo Viewer。 |
| `viewer` | `update_frequency_hz` | Viewer 刷新频率，单位为 Hz。 |
| `viewer` | `distance`、`lookat`、`azimuth`、`elevation` | 自由视角相机位姿。 |

## 控制模式

| 模式 | 控制范围 |
| --- | --- |
| `default` | 等价于 `whole`。 |
| `whole` | `/JOINTS_CMD` 控制全部 MuJoCo 执行器。 |
| `upper` | `/JOINTS_CMD` 控制腰部和双臂；浮动基座及下半身关节由模型约束固定。 |

命令超时后，whole 模式继续推进物理仿真并向全部执行器输出 0 力矩；upper 模式暂停物理仿真，保持超时时刻的实际姿态。upper 模式收到新的有效控制命令后恢复仿真；暂停期间的全零命令不会触发恢复。

## 场景组合

[`scene.xml`](scene.xml) 是默认配置选择的完整 MJCF 场景：

```xml
<include file="model/dr02_pro.xml"/>
<include file="../worlds/basic/basic.xml"/>
<include file="../worlds/demo/demo.xml"/>
```

- `model/dr02_pro.xml`：DR02 Pro 简化碰撞 MuJoCo 模型。
- `worlds/basic/basic.xml`：公共天空、灯光和可碰撞地面。
- `worlds/demo/demo.xml`：可选的仓库自带建筑、楼梯、地形和环境资源。

如不需要 demo 地形，可仅删除或注释第三个 include；基础环境应继续保留，以提供地面和灯光。需要使用自定义 world 时，可将第三个 include 替换为自定义 world XML。include 路径相对于 `scene.xml`；自定义 world 资源应放在 `worlds/` 下，不应修改机器人模型。需要选择其他完整场景时，修改 `config.yaml` 中的 `scene`。

whole 模式必须使用带碰撞地面的 world。upper 模式可以仅加载机器人模型和基础环境。

## Topic

| 方向 | Topic | 类型 |
| --- | --- | --- |
| SDK 到仿真 | `/JOINTS_CMD` | `drdds/msg/JointsCmd` |
| 仿真到 SDK | `/JOINTS_DATA` | `drdds/msg/Joints` |
| 仿真到 SDK | `/IMU_DATA_HEAD` | `sensor_msgs/msg/Imu` |
| 仿真到 SDK | `/IMU_DATA_BASE` | `sensor_msgs/msg/Imu` |

当前仿真将模型中的 Base IMU 数据同时发布到两个 IMU Topic，两条消息的坐标系均为 `base_link`。

SDK 定义 31 个关节，MuJoCo 模型包含 29 个执行器。最后两个 SDK 关节为虚拟关节，状态发布时填充为 0，不复制任何物理关节状态。
