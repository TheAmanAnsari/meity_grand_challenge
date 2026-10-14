# MeitY Grand Challenge: Simulation Environment

A ready-to-run simulation environment for the challenge: ROS 2 Humble, Gazebo
Harmonic, ArduPilot SITL, PX4 SITL, and the
[uavsim](https://github.com/NirmanJaiswal36/uavsim) simulator, all packaged
into a single Docker image. You do not need to install ROS, Gazebo, or any
autopilot software yourself, the container has everything pre-built.

## Repo layout

```
.devcontainer/   devcontainer.json, Dockerfile, postCreate.sh
uavsim/          simulator snapshot (scenarios, models, plugins)
test/            your controller / mission code goes here
start_container.sh   start/attach to the environment
run_sim.sh            launch a scenario
stop_sim.sh           stop a scenario
```

## Requirements

- Ubuntu 22.04 LTS (recommended, tested)
- Docker Engine, installed and running
- About 10 to 20 GB free disk space
- An internet connection for the first run, to pull the image

### Installing Docker

If you don't already have Docker Engine installed, the quickest way is Docker's official convenience script:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

Then add your user to the `docker` group, so you don't need `sudo` for every Docker command, and log out and back in (or reboot) for it to take effect:

```bash
sudo usermod -aG docker $USER
```

Confirm it's working:

```bash
docker run hello-world
```

For other operating systems, or if you'd rather follow the official guide,
see [docs.docker.com/engine/install](https://docs.docker.com/engine/install/).

## Install nvidia container runtime (optional, but recommended)
Installing this will allow for rendering of simulations with the dedicated nvidia graphics card if present, speeding up simulations by a large factor.
Follow the guide here https://developer.nvidia.com/nvidia-container-runtime

## Getting started

Fork this repository, and perform git clone:

```bash
git clone https://github.com/[your-username]/meity_grand_challenge.git
cd meity_grand_challenge
```


### Setup

1. Make the helper scripts executable (one-time):
   ```bash
   chmod +x start_container.sh run_sim.sh stop_sim.sh
   ```
2. Start the environment:
   ```bash
   ./start_container.sh
   ```
   On the first run, this pulls the image from Docker Hub and sets up the
   workspace — this can take a while depending on your connection. On every run after, it reattaches instantly to the same container.
3. Run `./start_container.sh` again from a second terminal any time you want
   another shell inside the same environment.


## Running a simulation

With the environment up, from your host terminal:

```bash
./run_sim.sh                                    # default scenario (forest_rescue) 
```

To stop a running simulation:

```bash
./stop_sim.sh                                   # default scenario
```

