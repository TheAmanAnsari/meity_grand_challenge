FROM osrf/ros:humble-desktop

# Add ubuntu user with same UID and GID as your host system, if it doesn't already exist
# Since Ubuntu 24.04, a non-root user is created by default with the name vscode and UID=1000
ARG USERNAME=meitychallenge
ARG USER_UID=1000
ARG USER_GID=$USER_UID
RUN if ! id -u $USER_UID >/dev/null 2>&1; then \
        groupadd --gid $USER_GID $USERNAME && \
        useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME; \
    fi
# Add sudo support for the non-root user
RUN apt-get update && \
    apt-get install -y sudo && \
    echo "$USERNAME ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME && \
    chmod 0440 /etc/sudoers.d/$USERNAME

# Switch from root to user
USER $USERNAME

# Add user to video group to allow access to webcam
RUN sudo usermod --append --groups video $USERNAME

# Update all packages
RUN sudo apt update && sudo apt upgrade -y

# Install Git
RUN sudo apt install -y git wget

# Rosdep update
RUN rosdep update

# Source the ROS setup file
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc

################################
## ADD ANY CUSTOM SETUP BELOW ##
################################

# Gazebo Harmonic
RUN sudo wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
    | sudo tee /etc/apt/sources.list.d/gazebo-stable.list

RUN sudo apt update && sudo apt install -y \
    gz-harmonic \
    libgz-sim8-dev rapidjson-dev \
    libopencv-dev libgstreamer1.0-dev \
    libgstreamer-plugins-base1.0-dev \
    gstreamer1.0-plugins-bad gstreamer1.0-libav gstreamer1.0-gl \
    python3-gz-transport13 python3-gz-msgs10

# Headless Rendering
RUN sudo apt update && sudo apt install -y \
    mesa-utils \
    libgl1-mesa-dri \
    libglx-mesa0 \
    libosmesa6 \
    xvfb

# ros_gz bridge (for Harmonic version)
ENV GZ_VERSION=harmonic
ENV LIBGL_ALWAYS_SOFTWARE=1
RUN sudo apt update && sudo apt install -y ros-humble-ros-gzharmonic

# Ardupilot SITL
ARG ARDUPILOT_TAG=Copter-4.7.1
ENV ARDUPILOT_ROOT=/home/${USERNAME}/ardupilot
ENV USER=${USERNAME}

RUN git clone --recurse-submodules --shallow-submodules --depth 1 \
    --branch ${ARDUPILOT_TAG} \
    https://github.com/ArduPilot/ardupilot.git ${ARDUPILOT_ROOT}

RUN cd ${ARDUPILOT_ROOT} && \
    Tools/environment_install/install-prereqs-ubuntu.sh -y

RUN cd ${ARDUPILOT_ROOT} && \
    ./waf configure --board sitl && \
    ./waf copter && \
    ./waf plane

RUN echo 'export PATH="$HOME/ardupilot/Tools/autotest:$PATH"' >> ~/.bashrc

# PX4 SITL
ARG PX4_TAG=v1.17.0
ENV PX4_ROOT=/home/${USERNAME}/PX4-Autopilot

RUN git clone --recurse-submodules --shallow-submodules --depth 1 \
    --branch ${PX4_TAG} \
    https://github.com/PX4/PX4-Autopilot.git ${PX4_ROOT}

RUN cd ${PX4_ROOT} && \
    bash ./Tools/setup/ubuntu.sh --no-nuttx

RUN cd ${PX4_ROOT} && \
    DONT_RUN=1 make px4_sitl_default

# MicroXRCEAgent
RUN git clone -b v2.4.3 https://github.com/eProsima/Micro-XRCE-DDS-Agent.git /home/${USERNAME}/Micro-XRCE-DDS-Agent \
    && cd /home/${USERNAME}/Micro-XRCE-DDS-Agent \
    && mkdir build && cd build \
    && cmake .. \
    && make -j$(nproc) \
    && sudo make install \
    && sudo ldconfig /usr/local/lib/