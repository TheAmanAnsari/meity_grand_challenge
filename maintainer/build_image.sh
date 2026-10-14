#!/bin/bash
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCKERHUB_USER="theamanansari"
IMAGE_REPO="meity-uav-challenge"
VERSION_TAG="${1:-latest}"

echo "Building image from ${REPO_ROOT}/.devcontainer/Dockerfile ..."
docker build \
    -f "${REPO_ROOT}/.devcontainer/Dockerfile" \
    -t "${DOCKERHUB_USER}/${IMAGE_REPO}:latest" \
    -t "${DOCKERHUB_USER}/${IMAGE_REPO}:${VERSION_TAG}" \
    "${REPO_ROOT}/.devcontainer"

echo ""
echo "Build complete. Tagged as:"
echo "  ${DOCKERHUB_USER}/${IMAGE_REPO}:latest"
echo "  ${DOCKERHUB_USER}/${IMAGE_REPO}:${VERSION_TAG}"
echo ""
read -p "Push both tags to Docker Hub now? [y/N] " CONFIRM
if [[ "${CONFIRM}" =~ ^[Yy]$ ]]; then
    docker push "${DOCKERHUB_USER}/${IMAGE_REPO}:latest"
    docker push "${DOCKERHUB_USER}/${IMAGE_REPO}:${VERSION_TAG}"
    echo "Pushed."
else
    echo "Skipped push. Run manually when ready:"
    echo "  docker push ${DOCKERHUB_USER}/${IMAGE_REPO}:latest"
    echo "  docker push ${DOCKERHUB_USER}/${IMAGE_REPO}:${VERSION_TAG}"
fi