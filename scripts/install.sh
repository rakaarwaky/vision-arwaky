#!/bin/bash
set -e

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DIST_DIR="$BASE_DIR/dist"
VENV_DIR="$DIST_DIR/venv"

echo ">>> Creating virtualenv..."
uv venv "$VENV_DIR" --clear

echo ">>> Installing vision-arwaky in virtualenv..."
uv pip install --python "$VENV_DIR/bin/python" -e "$BASE_DIR" --no-deps

echo ">>> Symlinking cv2 + numpy from global..."
ln -sf /home/raka/.local/lib/python3.14/site-packages/cv2 "$VENV_DIR/lib/python3.14/site-packages/cv2" 2>/dev/null || true
ln -sf /home/raka/.local/lib/python3.14/site-packages/numpy* "$VENV_DIR/lib/python3.14/site-packages/" 2>/dev/null || true

echo ">>> Installing lightweight runtime deps..."
uv pip install --python "$VENV_DIR/bin/python" fastmcp pydantic mcp requests pyyaml pillow 2>&1 | tail -3

# Optional ROCm check omitted (not needed for wrapper)

echo ">>> Done! Virtualenv in $VENV_DIR"
echo ">>> Run: $VENV_DIR/bin/vision-arwaky-mcp"
