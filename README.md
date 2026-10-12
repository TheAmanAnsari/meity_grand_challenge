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

- Ubuntu 22.04 LTS (other Linux distros may work but aren't officially tested)
- Docker Engine, installed and running
- About 10 GB free disk space (the image is pre-built, so no local compiling
  is needed)
- An internet connection for the first run, to pull the image
- X11 (already present on a standard Ubuntu desktop) for the simulator's GUI

### Installing Docker

If you don't already have Docker Engine installed, the quickest way is
Docker's official convenience script:

```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

Then add your user to the `docker` group, so you don't need `sudo` for every
Docker command, and log out and back in (or reboot) for it to take effect:

```bash
sudo usermod -aG docker $USER
```

Confirm it's working:

```bash
docker run hello-world
```

For other operating systems, or if you'd rather follow the official guide,
see [docs.docker.com/engine/install](https://docs.docker.com/engine/install/).

## Getting started

Clone this repo first, either way:

```bash
git clone https://github.com/TheAmanAnsari/meity_grand_challenge.git
cd meity_grand_challenge
```

You can then use either of the two paths below — pick whichever fits how
you work. You don't need both.

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

### Setup (VS Code)

1. Install the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   extension in VS Code.
2. Open the cloned folder in VS Code:
   ```bash
   code .
   ```
3. Click **Reopen in Container** when prompted (or Command Palette →
   **Dev Containers: Reopen in Container**).
4. VS Code pulls the pre-built image and sets up the workspace automatically.
   This takes a few minutes on the first run (downloading the image), and
   seconds on every run after that.
5. Use the integrated terminal inside VS Code for everything from here on.

## Running a simulation

With the environment up, from your host terminal:

```bash
./run_sim.sh                              # default forest_rescue scenario
./run_sim.sh scenarios/forest_static.yaml # specific scenario
```

If you're working inside a VS Code integrated terminal instead, run it
directly:

```bash
cd uavsim
./bin/uavsim up scenarios/forest_rescue.yaml
```

To stop a running simulation:

```bash
./stop_sim.sh                              # default scenario
./stop_sim.sh scenarios/forest_static.yaml # specific scenario
```

or, from inside the container:

```bash
cd uavsim
./bin/uavsim down scenarios/forest_rescue.yaml --gazebo
```

