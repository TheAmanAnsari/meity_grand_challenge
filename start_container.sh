#!/bin/bash
set -e

IMAGE_NAME="theamanansari/meity-uav-challenge:latest"
CONTAINER_NAME="meity_uav_challenge"
WORKSPACE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Allow the container to draw on screen
xhost +local:docker >/dev/null 2>&1 || true

if docker container inspect "${CONTAINER_NAME}" >/dev/null 2>&1; then
    STATUS=$(docker container inspect -f '{{.State.Status}}' "${CONTAINER_NAME}")
    if [ "${STATUS}" != "running" ]; then
        echo "Starting existing container '${CONTAINER_NAME}'..."
        docker start "${CONTAINER_NAME}" >/dev/null
    fi
    echo "Attaching to '${CONTAINER_NAME}'..."
    docker exec -it "${CONTAINER_NAME}" bash
else
    echo "Creating container '${CONTAINER_NAME}' from image '${IMAGE_NAME}'..."
    docker run -it \
        --name "${CONTAINER_NAME}" \
        --privileged \
        --network host \
        -e DISPLAY="${DISPLAY}" \
        -e QT_X11_NO_MITSHM=1 \
        -e LIBGL_ALWAYS_SOFTWARE=1 \
        -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
        -v "${WORKSPACE_DIR}:/workspace" \
        -w /workspace \
        "${IMAGE_NAME}" \
        bash -c "bash .devcontainer/postCreate.sh && bash"
fi