#!/usr/bin/env bash
# scripts/install.sh — Standard install entrypoint for vision-arwaky
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/install.local.sh" "$@"
