#!/bin/bash
set -e

BASE_DIR="/home/raka/.hermes/profiles/linus/workspace/vision-arwaky"
DIST_DIR="$BASE_DIR/dist"

echo ">>> Creating virtualenv..."
uv venv "$DIST_DIR/venv" --clear

echo ">>> Installing vision-arwaky in virtualenv..."
uv pip install --python "$DIST_DIR/venv/bin/python" -e "$BASE_DIR" --no-deps

echo ">>> Symlinking cv2 + numpy from global..."
ln -sf /home/raka/.local/lib/python3.14/site-packages/cv2 "$DIST_DIR/venv/lib/python3.14/site-packages/cv2" 2>/dev/null
ln -sf /home/raka/.local/lib/python3.14/site-packages/numpy* "$DIST_DIR/venv/lib/python3.14/site-packages/" 2>/dev/null

echo ">>> Installing lightweight runtime deps..."
uv pip install --python "$DIST_DIR/venv/bin/python" fastmcp pydantic mcp requests pyyaml pillow 2>&1 | tail -3

echo ">>> Checking bundled ROCm binary..."
if [ -f "$BASE_DIR/llama-server-rocm/llama-server" ]; then
    echo "✓ Bundled ROCm binary found"
else
    echo "⚠ Bundled ROCm binary not found. Vision AI will use fallback mode."
    echo "  To add: place the llama.cpp ROCm build in $BASE_DIR/llama-server-rocm/"
fi

echo ">>> Done! Virtualenv in $DIST_DIR/venv"
echo ">>> Run: $DIST_DIR/venv/bin/vision-arwaky-mcp"
echo ">>> Run: $DIST_DIR/venv/bin/vision-arwaky-cli"
echo ">>> Run: $DIST_DIR/venv/bin/vision-arwaky-tui"
