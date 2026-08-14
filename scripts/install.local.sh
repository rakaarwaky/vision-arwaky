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
if "$VENV_PIP" install -e ".[native]" 2>&1 | tail -4; then
    echo -e "${GREEN}✓ Package + native deps installed into venv${NC}"
else
    # llama-cpp-python (native backend only) may fail to build on this
    # Python/platform. Fall back to core deps so the external/CLI path works.
    echo -e "${YELLOW}⚠ native extra (llama-cpp-python) failed to build — installing core only${NC}"
    "$VENV_PIP" install -e . 2>&1 | tail -4
    echo -e "${GREEN}✓ Package (core deps) installed into venv${NC}"
    echo -e "${YELLOW}  Note: backend: native requires llama-cpp-python separately.${NC}"
fi

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
"$VENV_PY" -c "import llama_cpp" 2>/dev/null || DEPS_MISSING+=("llama-cpp-python")
command -v ffmpeg &>/dev/null || DEPS_MISSING+=("ffmpeg (binary)")

# ── GPU backend detection ───────────────────────────────
if command -v nvidia-smi &>/dev/null; then
    echo -e "${GREEN}✓ NVIDIA/CUDA detected${NC}"
elif command -v rocm-smi &>/dev/null || [ -d /opt/rocm ]; then
    echo -e "${GREEN}✓ AMD/ROCm detected${NC}"
else
    echo -e "${YELLOW}⚠ No GPU backend detected${NC}"
fi

# ── Build ROCm binary if needed ──────────────────────────
ROCM_BIN_DIR="$PROJECT_DIR/llama-server-rocm"
ROCM_BIN="$ROCM_BIN_DIR/llama-server"
if [ ! -f "$ROCM_BIN" ] && { command -v rocm-smi &>/dev/null || [ -d /opt/rocm ]; }; then
    echo -e "${YELLOW}  ROCm detected, building llama-server binary...${NC}"
    mkdir -p "$ROCM_BIN_DIR"
    
    LLAMA_CPP_DIR="$PROJECT_DIR/llama.cpp"
    if [ ! -d "$LLAMA_CPP_DIR" ]; then
        git clone --depth 1 https://github.com/ggerganov/llama.cpp.git "$LLAMA_CPP_DIR"
    fi
    
    cd "$LLAMA_CPP_DIR"
    mkdir -p build && cd build
    
    ROCM_GFX=$(rocminfo 2>/dev/null | grep "Name:" | grep -o 'gfx[0-9a-z]*' | head -1)
    if [ -z "$ROCM_GFX" ]; then
        ROCM_GFX="gfx1100"
    fi
    
    cmake .. -DCMAKE_BUILD_TYPE=Release -DGGML_HIP=ON -DAMDGPU_TARGETS="$ROCM_GFX"
    cmake --build . --config Release --target llama-server -j$(nproc)
    
    cp bin/llama-server "$ROCM_BIN"
    cd "$PROJECT_DIR"
    echo -e "${GREEN}✓ ROCm binary built at $ROCM_BIN${NC}"
fi

# Check bundled ROCm binary
if [ -f "$ROCM_BIN" ]; then
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
