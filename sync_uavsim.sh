#!/bin/bash
set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UAVSIM_DIR="${REPO_ROOT}/uavsim"
TEMP_DIR="$(mktemp -d)"

echo "Cloning latest uavsim..."
git clone https://github.com/NirmanJaiswal36/uavsim.git "${TEMP_DIR}"

COMMIT_HASH=$(git -C "${TEMP_DIR}" log -1 --format=%H)
echo "Latest commit: ${COMMIT_HASH}"

rm -rf "${TEMP_DIR}/.git"
rm -rf "${TEMP_DIR}/build"

echo "Syncing files into ${UAVSIM_DIR}..."
rsync -a --delete "${TEMP_DIR}/" "${UAVSIM_DIR}/"

rm -rf "${TEMP_DIR}"

echo ""
echo "Done. uavsim updated to commit ${COMMIT_HASH}."
echo "Review changes with: git status / git diff"
echo "Update README's pinned commit note to: ${COMMIT_HASH}"