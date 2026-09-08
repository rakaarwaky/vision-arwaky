#!/usr/bin/env bash
# scripts/uninstall.sh — Clean uninstaller for vision-arwaky (XDG Base Directory)
set -euo pipefail

BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/vision-arwaky"
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/vision-arwaky"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/vision-arwaky"
STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/vision-arwaky"
VENV_DIR="$DATA_DIR/venv"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=== Uninstalling vision-arwaky ==="

# Remove bin symlinks (full name + short alias + extras)
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

# Remove XDG config & cache (selalu), data & state saat --purge
if [ -d "$CONFIG_DIR" ]; then
    rm -rf "$CONFIG_DIR"
    echo "✓ Removed $CONFIG_DIR"
fi
if [ -d "$CACHE_DIR" ]; then
    rm -rf "$CACHE_DIR"
    echo "✓ Removed $CACHE_DIR"
fi
if [[ "${1:-}" == "--purge" ]]; then
    for d in "$DATA_DIR" "$STATE_DIR"; do
        if [ -d "$d" ]; then
            rm -rf "$d"
            echo "✓ Purged $d"
        fi
    done
fi

echo "Uninstall complete."
