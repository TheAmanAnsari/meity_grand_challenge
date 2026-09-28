# MeitY Grand Challenge: Simulation Environment

A reproducible dev container for the challenge: ROS 2 Humble, Gazebo Harmonic, ArduPilot SITL, PX4 SITL, and the [uavsim](https://github.com/NirmanJaiswal36/uavsim) simulator.

## Versions

| Component | Version |
|---|---|
| Base image | osrf/ros:humble-desktop |
| Gazebo | Harmonic (Gazebo Sim 8) |
| ArduPilot | Copter-4.7.1 |
| PX4-Autopilot | v1.17.0 |
| Micro-XRCE-DDS-Agent | v2.4.3 |


## Requirements

- Ubuntu 22.04 LTS
- Docker Engine, running
- VS Code with the Dev Containers extension
- About 15-20 GB free disk space
- Good internet connection for the first build
- About 45-60 minutes for the first build (as it compiles ArduPilot and PX4)

## Setup

1. Clone this repo and open it in VS Code:
```bash
   git clone https://github.com/TheAmanAnsari/meity_grand_challenge.git
   cd meity_grand_challenge
   code .
```
2. Click **Reopen in Container** when prompted (or Command Palette →
   **Dev Containers: Reopen in Container**), then wait for the build.
3. If GUI windows don't appear, run this once per login on your host
   (not inside the container):
```bash
   xhost +local:docker
```
4. Verify the environment inside the container:
```bash
   gz sim --version
   which sim_vehicle.py
   ls ${PX4_ROOT}/build/px4_sitl_default/bin/px4
   which MicroXRCEAgent
   ros2 pkg list | grep ros_gz
```
5. Run a scenario:
```bash
   cd uavsim
   ./bin/uavsim up scenarios/forest_rescue.yaml
```
