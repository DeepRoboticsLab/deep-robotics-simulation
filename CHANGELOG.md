# Changelog

## 1.2.0 - 2026-10-28

- Changed the QoS of `/JOINTS_DATA`, `/IMU_DATA_HEAD`, and `/IMU_DATA_BASE` publishers to Best Effort reliability and Keep Last history with a queue depth of 1.
- Older SDK versions using Reliable subscriptions cannot receive these Topics. Use DR02 Pro SDK 1.4.0 or later, or DR02 Std SDK 1.3.0 or later.

## 1.1.1 - 2026-08-24

- Removed the unused `dr02_pro/model/dr02_pro.urdf`. The URDF in `deep_robotics_model` is the reference version.

## 1.1.0 - 2026-08-07

- Added DR02 Std simulation support, including its 21-joint MuJoCo model and Base IMU output.

## 1.0.0

- Initial public repository structure for the DR02 Pro MuJoCo simulation.
