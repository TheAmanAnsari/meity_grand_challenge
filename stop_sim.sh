#!/bin/bash
set -e

CONTAINER_NAME="meity_uav_challenge"
SCENARIO="${1:-scenarios/forest_rescue.yaml}"

if ! docker container inspect "${CONTAINER_NAME}" >/dev/null 2>&1; then
    echo "Container '${CONTAINER_NAME}' doesn't exist. Nothing to stop."
    exit 0
fi

STATUS=$(docker container inspect -f '{{.State.Status}}' "${CONTAINER_NAME}")
if [ "${STATUS}" != "running" ]; then
    echo "Container '${CONTAINER_NAME}' isn't running. Nothing to stop."
    exit 0
fi

if ! docker exec "${CONTAINER_NAME}" pgrep -f "gz sim" >/dev/null 2>&1; then
    echo "No simulation is currently running. Nothing to stop."
    exit 0
fi

echo "Stopping scenario.. ${SCENARIO}"
docker exec -it "${CONTAINER_NAME}" bash -c "source /opt/ros/humble/setup.bash && cd uavsim && ./bin/uavsim down ${SCENARIO} --gazebo"