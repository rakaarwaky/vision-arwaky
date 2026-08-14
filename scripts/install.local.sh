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
echo -e "${YELLOW}[2/5]${NC} Creating XDG directories..."
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/vision-arwaky"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/vision-arwaky"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/vision-arwaky/memory"
VENV_DIR="$DATA_DIR/venv"
BIN_DIR="$HOME/.local/bin"
mkdir -p "$CONFIG_DIR" "$DATA_DIR" "$CACHE_DIR" "$BIN_DIR"
echo -e "${GREEN}✓ config : ${CONFIG_DIR}${NC}"
echo -e "${GREEN}✓ data  : ${DATA_DIR}${NC}"
echo -e "${GREEN}✓ cache : ${CACHE_DIR}${NC}"
echo -e "${GREEN}✓ venv  : ${VENV_DIR}${NC}"

# Copy default config if not exists
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
    if [ -f "$PROJECT_DIR/config.yaml" ]; then
        cp "$PROJECT_DIR/config.yaml" "$CONFIG_DIR/config.yaml"
        echo -e "${GREEN}✓ Default config copied to $CONFIG_DIR/config.yaml${NC}"
    fi
else
    echo -e "${GREEN}✓ Config already exists at $CONFIG_DIR/config.yaml${NC}"
fi

# ── Create isolated venv (do not touch system Python) ─────
echo ""
echo -e "${YELLOW}[3/5]${NC} Creating isolated virtualenv in XDG data dir..."
if [ ! -x "$VENV_DIR/bin/python" ]; then
    "$PYTHON" -m venv "$VENV_DIR"
    echo -e "${GREEN}✓ venv created${NC}"
else
    echo -e "${GREEN}✓ venv already exists${NC}"
fi
VENV_PY="$VENV_DIR/bin/python"
VENV_PIP="$VENV_DIR/bin/pip"
"$VENV_PY" -m pip install --upgrade pip wheel setuptools 2>&1 | tail -1

# ── Install package + deps into venv ──────────────────────
echo ""
echo -e "${YELLOW}[4/5]${NC} Installing vision-arwaky (editable) + dependencies into venv..."
"$VENV_PIP" install -e . 2>&1 | tail -4
echo -e "${GREEN}✓ Package + dependencies installed into venv${NC}"

# Expose entry points on PATH via symlinks into ~/.local/bin
for ep in vision-arwaky-cli vision-arwaky-mcp vision-arwaky-tui; do
    if [ -x "$VENV_DIR/bin/$ep" ]; then
        ln -sf "$VENV_DIR/bin/$ep" "$BIN_DIR/$ep"
    fi
done

# ── Verify CLI ─────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[5/5]${NC} Verifying CLI entry points..."
if [ -x "$BIN_DIR/vision-arwaky-cli" ]; then
    echo -e "${GREEN}✓ vision-arwaky-cli — $("$BIN_DIR/vision-arwaky-cli" --help 2>&1 | head -1)${NC}"
else
    echo -e "${RED}✗ vision-arwaky-cli not found${NC}"
fi

if [ -x "$BIN_DIR/vision-arwaky-mcp" ]; then
    echo -e "${GREEN}✓ vision-arwaky-mcp — MCP server${NC}"
else
    echo -e "${RED}✗ vision-arwaky-mcp not found${NC}"
fi

if [ -x "$BIN_DIR/vision-arwaky-tui" ]; then
    echo -e "${GREEN}✓ vision-arwaky-tui — TUI config${NC}"
else
    echo -e "${RED}✗ vision-arwaky-tui not found${NC}"
fi

# ── Check deps ─────────────────────────────────────────────
echo ""
echo -e "${YELLOW}[6/6]${NC} Dependency check (against venv)..."
DEPS_MISSING=()

"$VENV_PY" -c "import cv2" 2>/dev/null || DEPS_MISSING+=("opencv-python")
"$VENV_PY" -c "import PIL" 2>/dev/null || DEPS_MISSING+=("pillow")
"$VENV_PY" -c "import pytesseract" 2>/dev/null || DEPS_MISSING+=("pytesseract")
command -v ffmpeg &>/dev/null || DEPS_MISSING+=("ffmpeg (binary)")

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
echo -e "${GREEN}  vision-arwaky installed (venv: ${VENV_DIR})!${NC}"
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
