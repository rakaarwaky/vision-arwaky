1|#!/usr/bin/env bash
2|# install.local.sh — Local development install for vision-arwaky
3|# Usage: ./scripts/install.local.sh
4|
5|set -euo pipefail
6|
7|RED='\033[0;31m'
8|GREEN='\033[0;32m'
9|YELLOW='\033[1;33m'
10|CYAN='\033[0;36m'
11|NC='\033[0m'
12|
13|PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
14|cd "$PROJECT_DIR"
15|
16|echo -e "${CYAN}══════════════════════════════════════════════${NC}"
17|echo -e "${CYAN}  vision-arwaky — Local Install${NC}"
18|echo -e "${CYAN}══════════════════════════════════════════════${NC}"
19|echo ""
20|
21|# ── Check Python ──────────────────────────────────────────
22|echo -e "${YELLOW}[1/5]${NC} Checking Python version..."
23|PYTHON="${PYTHON:-python3}"
24|if ! command -v "$PYTHON" &>/dev/null; then
25|    echo -e "${RED}✗ Python not found. Install Python 3.12+ first.${NC}"
26|    exit 1
27|fi
28|
29|$PYTHON -c "import sys; assert sys.version_info >= (3, 12), 'Python 3.12+ required'" 2>/dev/null || {
30|    echo -e "${RED}✗ Python 3.12+ required${NC}"
31|    exit 1
32|}
33|echo -e "${GREEN}✓ Python $($PYTHON --version)${NC}"
34|
35|# ── Create XDG dirs ───────────────────────────────────────
36|echo ""
37|echo -e "${YELLOW}[2/5]${NC} Creating config & cache directories..."
38|CONFIG_DIR="$HOME/.config/vision-arwaky"
39|CACHE_DIR="$HOME/.cache/vision-arwaky/memory"
40|mkdir -p "$CONFIG_DIR" "$CACHE_DIR"
41|echo -e "${GREEN}✓ ${CONFIG_DIR}${NC}"
42|echo -e "${GREEN}✓ ${CACHE_DIR}${NC}"
43|
44|# Copy default config if not exists
45|if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
46|    if [ -f "$PROJECT_DIR/config.yaml" ]; then
47|        cp "$PROJECT_DIR/config.yaml" "$CONFIG_DIR/config.yaml"
48|        echo -e "${GREEN}✓ Default config copied to $CONFIG_DIR/config.yaml${NC}"
49|    fi
50|else
51|    echo -e "${GREEN}✓ Config already exists at $CONFIG_DIR/config.yaml${NC}"
52|fi
53|
54|# ── Install package ───────────────────────────────────────
55|echo ""
56|echo -e "${YELLOW}[3/5]${NC} Installing vision-arwaky (editable, no deps)..."
57|pip install -e . --no-deps 2>&1 | tail -3
58|echo -e "${GREEN}✓ Package installed${NC}"
59|
60|# ── Verify CLI ─────────────────────────────────────────────
61|echo ""
62|echo -e "${YELLOW}[4/5]${NC} Verifying CLI entry points..."
63|if command -v vision-arwaky-cli &>/dev/null; then
64|    echo -e "${GREEN}✓ vision-arwaky-cli — $(vision-arwaky-cli --help 2>&1 | head -1)${NC}"
65|else
66|    echo -e "${RED}✗ vision-arwaky-cli not found in PATH${NC}"
67|fi
68|
69|if command -v vision-arwaky &>/dev/null; then
70|    echo -e "${GREEN}✓ vision-arwaky — MCP server${NC}"
71|else
72|    echo -e "${RED}✗ vision-arwaky not found in PATH${NC}"
73|fi
74|
75|if command -v vision-arwaky-tui &>/dev/null; then
76|    echo -e "${GREEN}✓ vision-arwaky-tui — TUI config${NC}"
77|else
78|    echo -e "${RED}✗ vision-arwaky-tui not found in PATH${NC}"
79|fi
80|
81|# ── Check deps ─────────────────────────────────────────────
82|echo ""
83|echo -e "${YELLOW}[5/5]${NC} Optional dependency check..."
84|DEPS_MISSING=()
85|
86|$PYTHON -c "import cv2" 2>/dev/null || DEPS_MISSING+=("opencv-python")
87|$PYTHON -c "import PIL" 2>/dev/null || DEPS_MISSING+=("pillow")
88|$PYTHON -c "import pytesseract" 2>/dev/null || DEPS_MISSING+=("pytesseract")
89|$PYTHON -c "import llama_cpp" 2>/dev/null || DEPS_MISSING+=("llama-cpp-python")
90|command -v ffmpeg &>/dev/null || DEPS_MISSING+=("ffmpeg (binary)")
91|
92|if [ ${#DEPS_MISSING[@]} -eq 0 ]; then
93|    echo -e "${GREEN}✓ All optional dependencies found${NC}"
94|else
95|    echo -e "${YELLOW}⚠ Missing optional deps:${NC}"
96|    for dep in "${DEPS_MISSING[@]}"; do
97|        echo "    - $dep"
98|    done
99|fi
100|
101|# ── Done ──────────────────────────────────────────────────
102|echo ""
103|echo -e "${CYAN}══════════════════════════════════════════════${NC}"
104|echo -e "${GREEN}  vision-arwaky v2.0.5 installed!${NC}"
105|echo -e "${CYAN}══════════════════════════════════════════════${NC}"
106|echo ""
107|echo -e "  ${GREEN}vision-arwaky-cli${NC}      — CLI interface"
108|echo -e "  ${GREEN}vision-arwaky${NC}   — MCP server"
109|echo -e "  ${GREEN}vision-arwaky-tui${NC}      — TUI config"
110|echo ""
111|echo -e "  Config:  ${YELLOW}~/.config/vision-arwaky/config.yaml${NC}"
112|echo -e "  Cache:   ${YELLOW}~/.cache/vision-arwaky/memory/${NC}"
113|echo ""
114|echo -e "  Quick start:"
115|echo -e "    ${CYAN}vision-arwaky-cli status${NC}"
116|echo ""
117|