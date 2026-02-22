#!/usr/bin/env bash
# Author: Aditya Dogra
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

python3 scripts/bootstrap.py "$@"
