#!/usr/bin/env bash
# scripts/uninstall.sh — Clean uninstaller for vision-arwaky
set -euo pipefail

BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/vision-arwaky"
VENV_DIR="$DATA_DIR/venv"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Uninstalling vision-arwaky ==="

# Remove bin symlinks
COMMANDS=("vision-arwaky" "vision-arwaky-cli" "vision-arwaky-mcp" "vision-arwaky-tui" "va")
for cmd in "${COMMANDS[@]}"; do
    if [ -L "$BIN_DIR/$cmd" ] || [ -f "$BIN_DIR/$cmd" ]; then
        rm -f "$BIN_DIR/$cmd"
        echo "✓ Removed $BIN_DIR/$cmd"
    fi
done

# Remove in-tree .venv symlink if it points to XDG
if [ -L "$PROJECT_DIR/.venv" ]; then
    rm -f "$PROJECT_DIR/.venv"
    echo "✓ Removed $PROJECT_DIR/.venv symlink"
fi

if [[ "${1:-}" == "--purge" ]]; then
    if [ -d "$DATA_DIR" ]; then
        rm -rf "$DATA_DIR"
        echo "✓ Purged $DATA_DIR"
    fi
fi

echo "Uninstall complete."
