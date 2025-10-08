#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR}/.."

pushd "$SCRIPT_DIR" >/dev/null

docker compose up --build

popd >/dev/null
