#!/usr/bin/env bash
# install.local.sh — Local development install for vision-arwaky
# Usage: ./scripts/install.local.sh

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_DIR"

echo -e "${CYAN}══════════════════════════════════════════════${NC}"
echo -e "${CYAN}  vision-arwaky — Local Install${NC}"
echo -e "${CYAN}══════════════════════════════════════════════${NC}"
echo ""

# ── Check Python ──────────────────────────────────────────
echo -e "${YELLOW}[1/5]${NC} Checking Python version..."
PYTHON="${PYTHON:-python3}"
if ! command -v "$PYTHON" &>/dev/null; then
    echo -e "${RED}✗ Python not found. Install Python 3.12+ first.${NC}"
    exit 1
fi

$PYTHON -c "import sys; assert sys.version_info >= (3, 12), 'Python 3.12+ required'" 2>/dev/null || {
    echo -e "${RED}✗ Python 3.12+ required${NC}"
    exit 1
}
echo -e "${GREEN}✓ Python $($PYTHON --version)${NC}"

# ── Create XDG dirs ───────────────────────────────────────
echo ""
echo -e "${YELLOW}[2/5]${NC} Creating config & cache directories..."
CONFIG_DIR="$HOME/.config/vision-arwaky"
CACHE_DIR="$HOME/.cache/vision-arwaky/memory"
mkdir -p "$CONFIG_DIR" "$CACHE_DIR"
echo -e "${GREEN}✓ ${CONFIG_DIR}${NC}"
echo -e "${GREEN}✓ ${CACHE_DIR}${NC}"

# Copy default config if not exists
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
    if [ -f "$PROJECT_DIR/config.yaml" ]; then
        cp "$PROJECT_DIR/config.yaml" "$CONFIG_DIR/config.yaml"
        echo -e "${GREEN}✓ Default config copied to $CONFIG_DIR/config.yaml${NC}"
    fi
else
    echo -e "${GREEN}✓ Config already exists at $CONFIG_DIR/config.yaml${NC}"
fi

# ── Install package ───────────────────────────────────────
echo ""
echo -e "${YELLOW}[3/5]${NC} Installing vision-arwaky (editable, no deps)..."
pip install -e . --no-deps 2>&1 | tail -3
echo -e "${GREEN}✓ Package installed${NC}"

# ── Verify CLI ─────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[4/5]${NC} Verifying CLI entry points..."
if command -v vision-arwaky-cli &>/dev/null; then
    echo -e "${GREEN}✓ vision-arwaky-cli — $(vision-arwaky-cli --help 2>&1 | head -1)${NC}"
else
    echo -e "${RED}✗ vision-arwaky-cli not found in PATH${NC}"
fi

if command -v vision-arwaky-mcp &>/dev/null; then
    echo -e "${GREEN}✓ vision-arwaky-mcp — MCP server${NC}"
else
    echo -e "${RED}✗ vision-arwaky-mcp not found in PATH${NC}"
fi

if command -v vision-arwaky-tui &>/dev/null; then
    echo -e "${GREEN}✓ vision-arwaky-tui — TUI config${NC}"
else
    echo -e "${RED}✗ vision-arwaky-tui not found in PATH${NC}"
fi

# ── Check deps ─────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[5/5]${NC} Optional dependency check..."
DEPS_MISSING=()

$PYTHON -c "import cv2" 2>/dev/null || DEPS_MISSING+=("opencv-python")
$PYTHON -c "import PIL" 2>/dev/null || DEPS_MISSING+=("pillow")
$PYTHON -c "import pytesseract" 2>/dev/null || DEPS_MISSING+=("pytesseract")
$PYTHON -c "import llama_cpp" 2>/dev/null || DEPS_MISSING+=("llama-cpp-python")
command -v ffmpeg &>/dev/null || DEPS_MISSING+=("ffmpeg (binary)")

# Check bundled ROCm binary
if [ -f "$PROJECT_DIR/llama-server-rocm/llama-server" ]; then
    echo -e "${GREEN}✓ bundled ROCm binary (llama-server)${NC}"
else
    echo -e "${YELLOW}⚠ bundled ROCm binary not found in llama-server-rocm/${NC}"
fi

# Check test fixtures
if [ -f "$PROJECT_DIR/tests/fixtures/test.jpeg" ] && [ -f "$PROJECT_DIR/tests/fixtures/test.mp4" ]; then
    echo -e "${GREEN}✓ test fixtures (test.jpeg + test.mp4)${NC}"
else
    echo -e "${YELLOW}⚠ test fixtures not complete${NC}"
fi

if [ ${#DEPS_MISSING[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ All optional dependencies found${NC}"
else
    echo -e "${YELLOW}⚠ Missing optional deps:${NC}"
    for dep in "${DEPS_MISSING[@]}"; do
        echo "    - $dep"
    done
fi

# ── Done ──────────────────────────────────────────────────
echo ""
echo -e "${CYAN}══════════════════════════════════════════════${NC}"
echo -e "${GREEN}  vision-arwaky v2.0.5 installed!${NC}"
echo -e "${CYAN}══════════════════════════════════════════════${NC}"
echo ""
echo -e "  ${GREEN}vision-arwaky-cli${NC}    — CLI interface"
echo -e "  ${GREEN}vision-arwaky-mcp${NC}    — MCP server"
echo -e "  ${GREEN}vision-arwaky-tui${NC}    — TUI config"
echo ""
echo -e "  Quick start:"
echo -e "    ${CYAN}vision-arwaky-cli test${NC}    — Run test suite"
echo -e "    ${CYAN}vision-arwaky-cli analyze --image foto.jpg --prompt \"Describe\"${NC}"
echo ""
