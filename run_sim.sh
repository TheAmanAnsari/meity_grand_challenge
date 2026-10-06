#!/bin/bash
set -e

CONTAINER_NAME="meity_uav_challenge"
SCENARIO="${1:-scenarios/forest_static.yaml}"

if ! docker container inspect "${CONTAINER_NAME}" >/dev/null 2>&1; then
    echo "Container '${CONTAINER_NAME}' doesn't exist yet."
    echo "Run ./start_container.sh first."
    exit 1
fi

STATUS=$(docker container inspect -f '{{.State.Status}}' "${CONTAINER_NAME}")
if [ "${STATUS}" != "running" ]; then
    echo "Starting container '${CONTAINER_NAME}'..."
    docker start "${CONTAINER_NAME}" >/dev/null
fi

echo "Launching scenario: ${SCENARIO}"
docker exec -it "${CONTAINER_NAME}" bash -c "source /opt/ros/humble/setup.bash && cd uavsim && ./bin/uavsim up ${SCENARIO}"