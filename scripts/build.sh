#!/bin/bash
set -e

BASE_DIR="/home/raka/mcp-arwaky/vision-arwaky"
DIST_DIR="$BASE_DIR/dist"

echo ">>> Creating virtualenv..."
uv venv "$DIST_DIR/venv" --clear

echo ">>> Installing vision-arwaky in virtualenv..."
uv pip install --python "$DIST_DIR/venv/bin/python" -e "$BASE_DIR" --no-deps

echo ">>> Installing runtime dependencies..."
uv pip install --python "$DIST_DIR/venv/bin/python" opencv-python pillow numpy requests pyyaml mcp fastmcp pydantic 2>&1 | tail -3

echo ">>> Done! Virtualenv in $DIST_DIR/venv"
echo ">>> Run: $DIST_DIR/venv/bin/vision-arwaky"
echo ">>> Run: $DIST_DIR/venv/bin/vision-cli"
