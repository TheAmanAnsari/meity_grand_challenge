#!/bin/bash
set -e

WORKSPACE_ROOT="$(pwd)"
UAVSIM_DIR="${WORKSPACE_ROOT}/uavsim"

echo "=== [postCreate] Installing uavsim Python dependencies ==="
pip3 install --user -r "${UAVSIM_DIR}/requirements.txt"

echo "=== [postCreate] Building uavsim gz_plugins (GZ_VERSION=${GZ_VERSION}) ==="
cmake -B "${UAVSIM_DIR}/build" -S "${UAVSIM_DIR}/gz_plugins"
cmake --build "${UAVSIM_DIR}/build" -j"$(nproc)"

echo "=== [postCreate] Setup complete ==="
