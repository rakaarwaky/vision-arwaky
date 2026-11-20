#!/usr/bin/env bash
# scripts/install.sh — Vision Arwaky Installer (XDG Base Directory)
# ==============================================================================
# All data, virtual environments, binaries, configs, caches, and logs strictly
# adhere to the Linux XDG Base Directory Specification:
#   - Binaries : $XDG_BIN_HOME    (default: ~/.local/bin)
#   - Data/Venv: $XDG_DATA_HOME   (default: ~/.local/share/vision-arwaky/venv)
#   - Config   : $XDG_CONFIG_HOME (default: ~/.config/vision-arwaky)
#   - Cache    : $XDG_CACHE_HOME  (default: ~/.cache/vision-arwaky)
#   - State/Log: $XDG_STATE_HOME  (default: ~/.local/state/vision-arwaky)
# ==============================================================================

set -euo pipefail

# Colors and formatting
RED=$'\033[0;31m'
GREEN=$'\033[0;32m'
YELLOW=$'\033[0;33m'
BLUE=$'\033[0;34m'
CYAN=$'\033[0;36m'
BOLD=$'\033[1m'
RESET=$'\033[0m'

# Helpers
info()    { printf "%s[i]%s %s\n" "$CYAN" "$RESET" "$*"; }
success() { printf "%s[✓]%s %s\n" "$GREEN" "$RESET" "$*"; }
warn()    { printf "%s[!]%s %s\n" "$YELLOW" "$RESET" "$*"; }
error()   { printf "%s[✗]%s %s\n" "$RED" "$RESET" "$*" >&2; }
header()  { printf "\n%s%s=== %s ===%s\n" "$BOLD" "$BLUE" "$*" "$RESET"; }

# Resolve Repository Root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

# XDG Base Directory Resolutions
# XDG-compliant precedence: a shell env var wins; otherwise the per-tool
# fallback below is used. (If you want a persistent default, export the
# XDG_*_HOME variables in your shell rc — that takes effect automatically.)
XDG_BIN_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
XDG_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/vision-arwaky"
XDG_DATA_ROOT="${XDG_DATA_HOME:-$HOME/.local/share}/vision-arwaky"
XDG_VENV_DIR="$XDG_DATA_ROOT/venv"
XDG_CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/vision-arwaky"
XDG_STATE_DIR="${XDG_STATE_HOME:-$HOME/.local/state}/vision-arwaky"

# Point uv at the XDG venv. uv sync (Step 4) creates the venv AND installs
# into it, so the package and all entry points (va, vision-arwaky, ...) end
# up in $XDG_VENV_DIR/bin. PYTHON_BIN is defaulted below and re-applied to
# UV_PYTHON after argument parsing (so --python works).
export UV_PROJECT_ENVIRONMENT="$XDG_VENV_DIR"

# Configuration variables & Defaults
DEV_MODE=0
REINSTALL=0
CREATE_SYMLINKS=1
CHECK_ONLY=0
BIN_DIR="$XDG_BIN_DIR"
VENV_DIR="$XDG_VENV_DIR"
PYTHON_BIN="python3"

show_help() {
    cat << 'EOF'
Vision Arwaky - Automated Installer (Strict XDG Standard)

Usage:
  ./scripts/install.sh [OPTIONS]

Options:
  --dev             Install developer & test dependencies (pytest, ruff, mypy, etc.)
  --reinstall       Clean existing XDG installation and reinstall completely from scratch
  --no-symlink      Do not create symlinks in ~/.local/bin
  --bin-dir <path>  Target directory for CLI symlinks (default: $XDG_BIN_HOME or ~/.local/bin)
  --python <path>   Path to Python 3 binary (default: python3)
  --check-only      Run prerequisite checks only and exit
  -h, --help        Show this help message and exit

XDG Base Directory Layout:
  Binaries     : $XDG_BIN_HOME    -> ~/.local/bin
  Venv & Data  : $XDG_DATA_HOME   -> ~/.local/share/vision-arwaky/venv
  Config       : $XDG_CONFIG_HOME -> ~/.config/vision-arwaky
  Cache        : $XDG_CACHE_HOME  -> ~/.cache/vision-arwaky
  Logs & State : $XDG_STATE_HOME  -> ~/.local/state/vision-arwaky

Examples:
  ./scripts/install.sh                # Install Vision Arwaky into XDG paths
  ./scripts/install.sh --reinstall    # Purge old install and reinstall cleanly
  ./scripts/install.sh --dev          # Install with developer tools
EOF
    exit 0
}

# Parse Command Line Arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --dev)
            DEV_MODE=1
            shift
            ;;
        --reinstall|--clean)
            REINSTALL=1
            shift
            ;;
        --no-symlink)
            CREATE_SYMLINKS=0
            shift
            ;;
        --bin-dir)
            if [[ -z "${2:-}" ]]; then
                error "Argument --bin-dir requires a path"
                exit 1
            fi
            BIN_DIR="$2"
            shift 2
            ;;
        --python)
            if [[ -z "${2:-}" ]]; then
                error "Argument --python requires a binary name/path"
                exit 1
            fi
            PYTHON_BIN="$2"
            shift 2
            ;;
        --check-only)
            CHECK_ONLY=1
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            error "Unknown option: $1"
            echo "Run './scripts/install.sh --help' for usage instructions."
            exit 1
            ;;
    esac
done

# Re-apply the user's Python to uv so Step 4 uses the interpreter from --python
# (or the default python3). This runs before any step that invokes uv.
export UV_PYTHON="${PYTHON_BIN}"

printf "\n%s%s" "$BOLD" "$CYAN"
cat << 'EOF'
  _    _ _     _                   _                           _            
 | |  | (_)   (_)                 / \   _ ____      ____ _ | | ___   _  
 | |  | | |__  _  ___  _ __      / _ \ | '__\ \ /\ / / _` || |/ / | | | 
 \ \  / /| '_ \| |/ _ \| '_ \    / ___ \| |   \ V  V / (_| ||   <| |_| | 
  \_\/_/ |_| |_|_|\___/|_| |_|  /_/   \_\_|    \_/\_/ \__,_||_|\_\\__, | 
                                                                   |___/  
EOF
printf "%s" "$RESET"
printf "%sInstaller for Vision Arwaky Engine (Strict XDG)%s\n" "$BOLD" "$RESET"
printf "Repo: %s\n\n" "$REPO_ROOT"

# ==============================================================================
# 1. System Prerequisite Checks
# ==============================================================================
header "1. Checking System Prerequisites"

MISSING_REQ=0

# OS check
OS_TYPE="$(uname -s)"
info "Operating System: $OS_TYPE ($(uname -m))"

# Check Python executable
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    error "Python executable '$PYTHON_BIN' not found."
    info "Please install Python 3 (>= 3.12):"
    echo "  - Ubuntu/Debian: sudo apt update && sudo apt install -y python3 python3-venv python3-pip"
    echo "  - Arch Linux:    sudo pacman -S python python-pip"
    echo "  - Fedora:        sudo dnf install python3 python3-pip"
    MISSING_REQ=1
else
    PY_VER_RAW="$("$PYTHON_BIN" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")' 2>/dev/null || echo "0.0.0")"
    PY_MAJOR="$("$PYTHON_BIN" -c 'import sys; print(sys.version_info.major)' 2>/dev/null || echo "0")"
    PY_MINOR="$("$PYTHON_BIN" -c 'import sys; print(sys.version_info.minor)' 2>/dev/null || echo "0")"

    if [[ "$PY_MAJOR" -lt 3 ]] || { [[ "$PY_MAJOR" -eq 3 ]] && [[ "$PY_MINOR" -lt 12 ]]; }; then
        error "Python version $PY_VER_RAW is too old. Requires Python >= 3.12."
        MISSING_REQ=1
    else
        success "Python found: $PYTHON_BIN (version $PY_VER_RAW)"
    fi
fi

# Check FFmpeg and Tesseract
if command -v ffmpeg >/dev/null 2>&1; then
    FFMPEG_VER="$(ffmpeg -version 2>&1 | sed -n '1p')"
    success "FFmpeg found: $FFMPEG_VER"
else
    warn "FFmpeg is not installed or not in PATH!"
    info "To install FFmpeg on Linux:"
    echo "  - Ubuntu/Debian: sudo apt update && sudo apt install -y ffmpeg"
    echo "  - Arch Linux:    sudo pacman -S ffmpeg"
    echo "  - Fedora:        sudo dnf install ffmpeg"
fi

if command -v tesseract >/dev/null 2>&1; then
    TESS_VER="$(tesseract --version 2>&1 | sed -n '1p')"
    success "Tesseract found: $TESS_VER"
else
    warn "Tesseract is not installed or not in PATH!"
    info "To install Tesseract on Linux:"
    echo "  - Ubuntu/Debian: sudo apt update && sudo apt install -y tesseract-ocr tesseract-ocr-eng"
    echo "  - Arch Linux:    sudo pacman -S tesseract tesseract-data-eng"
    echo "  - Fedora:        sudo dnf install tesseract tesseract-data-eng"
fi

# Check venv module capability
if [[ "$MISSING_REQ" -eq 0 ]]; then
    if ! "$PYTHON_BIN" -c "import venv" >/dev/null 2>&1; then
        error "Python 'venv' module is missing."
        info "Please install python3-venv:"
        echo "  - Ubuntu/Debian: sudo apt install -y python3-venv"
        MISSING_REQ=1
    else
        success "Python venv module is available"
    fi
fi

if [[ "$MISSING_REQ" -ne 0 ]]; then
    error "Cannot proceed due to missing prerequisite dependencies."
    exit 1
fi

if [[ "$CHECK_ONLY" -eq 1 ]]; then
    success "Prerequisite check completed successfully."
    exit 0
fi

# ==============================================================================
# 2. XDG Directory Structure Setup
# ==============================================================================
header "2. Initializing XDG Directories"

info "Creating standard XDG directories..."
mkdir -p "$XDG_CONFIG_DIR" "$XDG_DATA_ROOT" "$XDG_CACHE_DIR" "$XDG_STATE_DIR" "$BIN_DIR"
chmod 700 "$XDG_CONFIG_DIR" "$XDG_DATA_ROOT" "$XDG_CACHE_DIR" "$XDG_STATE_DIR" "$BIN_DIR"
success "XDG directories prepared:"
echo "  - Config : $XDG_CONFIG_DIR"
echo "  - Data   : $XDG_DATA_ROOT"
echo "  - Cache  : $XDG_CACHE_DIR"
echo "  - State  : $XDG_STATE_DIR"
echo "  - Bin    : $BIN_DIR"

# Copy default config if not exists
if [ ! -f "$XDG_CONFIG_DIR/config.yaml" ]; then
    if [ -f "$REPO_ROOT/config.yaml" ]; then
        cp "$REPO_ROOT/config.yaml" "$XDG_CONFIG_DIR/config.yaml"
        chmod 600 "$XDG_CONFIG_DIR/config.yaml"
        success "Default config copied to $XDG_CONFIG_DIR/config.yaml"
    fi
else
    success "Config already exists at $XDG_CONFIG_DIR/config.yaml"
fi

# ==============================================================================
# 3. uv availability check (uv owns the XDG venv end-to-end)
# ==============================================================================
header "3. Checking uv (the repo's package manager)"

if ! command -v uv >/dev/null 2>&1; then
    error "'uv' is required but not in PATH."
    info "Install it with one of:"
    echo "  - curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  - pip install uv"
    echo "  - Ubuntu/Debian: sudo apt install uv"
    exit 1
fi
UV_VER="$(uv --version 2>/dev/null || true)"
success "uv found: ${UV_VER:-$(command -v uv)}"

# Clean old in-tree .venv before setup
if [[ -e "$REPO_ROOT/.venv" ]] || [[ -L "$REPO_ROOT/.venv" ]]; then
    rm -rf "$REPO_ROOT/.venv"
fi

# ==============================================================================
# 4. Install into the XDG venv via uv sync
# ==============================================================================
# uv sync creates the venv at $UV_PROJECT_ENVIRONMENT (= $XDG_VENV_DIR) and
# installs the package editable into it, so all entry points (va,
# vision-arwaky-cli, ...) land in $XDG_VENV_DIR/bin. No separate venv step,
# no mixing python -m venv with uv pip. Fail loudly: a bad install must not
# fall through to a silent "all done".
header "4. Installing dependencies into the XDG venv ($XDG_VENV_DIR)"

if [[ "$REINSTALL" -eq 1 ]] && [[ -d "$XDG_VENV_DIR" ]]; then
    info "Purging existing XDG venv at $XDG_VENV_DIR (--reinstall)..."
    rm -rf "$XDG_VENV_DIR"
fi

SYNC_ARGS=(--frozen)
if [[ "$DEV_MODE" -eq 1 ]]; then
    SYNC_ARGS+=(--group dev)
    info "Installing with dev dependencies (--dev)."
else
    info "Installing the runtime dependencies."
fi

if ! uv sync "${SYNC_ARGS[@]}" --python "$PYTHON_BIN"; then
    error "uv sync failed. The XDG venv was not fully installed."
    info "Re-run with: $0 --reinstall   (or without --dev if that was the flag that failed)"
    exit 1
fi
success "uv sync complete — package installed into $XDG_VENV_DIR"

# ==============================================================================
# 5. CLI Symlinks Setup (~/.local/bin)
# ==============================================================================
if [[ "$CREATE_SYMLINKS" -eq 1 ]]; then
    header "5. Setting Up Global CLI Commands ($BIN_DIR)"
    mkdir -p "$BIN_DIR"

    # Map each CLI name to the executable that provides it. `va` and
    # `vision-arwaky` are aliases for the same CLI entry point.
    declare -A SRC_MAP=(
        [vision-arwaky-cli]=vision-arwaky-cli
        [vision-arwaky-mcp]=vision-arwaky-mcp
        [vision-arwaky-tui]=vision-arwaky-tui
        [va]=vision-arwaky-cli
        [vision-arwaky]=vision-arwaky-cli
    )

    MISSING_EXES=0
    for cmd in "vision-arwaky-cli" "vision-arwaky-mcp" "vision-arwaky-tui" "va" "vision-arwaky"; do
        SRC_EXE="$XDG_VENV_DIR/bin/${SRC_MAP[$cmd]}"
        DEST_EXE="$BIN_DIR/$cmd"
        if [[ -x "$SRC_EXE" ]]; then
            ln -sf "$SRC_EXE" "$DEST_EXE"
            success "Linked $DEST_EXE -> $SRC_EXE"
        else
            error "Expected executable not found: $SRC_EXE"
            info "uv sync succeeded but this CLI is missing — check for a failed build in Step 4."
            MISSING_EXES=1
        fi
    done

    if [[ "$MISSING_EXES" -eq 1 ]]; then
        error "Some CLI symlinks could not be created. Re-run with --reinstall."
        exit 1
    fi

    # Check if BIN_DIR is in PATH
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        warn "$BIN_DIR is not currently in your PATH!"
        info "To run vision-arwaky commands from any terminal, add this to your ~/.bashrc or ~/.zshrc:"
        printf "\n  %sexport PATH=\"%s:\$PATH\"%s\n\n" "$BOLD" "$BIN_DIR" "$RESET"
    else
        success "$BIN_DIR is already in your PATH"
    fi
fi

# ==============================================================================
# 6. Workspace Initialization (.vision-arwaky -> XDG, .venv -> XDG Venv)
# ==============================================================================
header "6. Initializing Workspace Symlink"

CLI_EXEC="$XDG_VENV_DIR/bin/vision-arwaky-cli"
if [[ -x "$CLI_EXEC" ]]; then
    info "Initializing workspace (.vision-arwaky, .venv symlink, .git/info/exclude)..."
    if ! "$CLI_EXEC" init "$REPO_ROOT"; then
        warn "workspace init returned a non-zero status — check the message above"
    else
        success "Local workspace initialized"
    fi
fi

# Ensure .env carries the UV_PROJECT_ENVIRONMENT so later `uv run` / `uv sync`
# invocations target the XDG venv, not a freshly created in-tree .venv.
if [[ ! -f "$REPO_ROOT/.env" ]] || ! grep -q "UV_PROJECT_ENVIRONMENT" "$REPO_ROOT/.env"; then
    {
        echo ""
        echo "# Written by scripts/install.sh — target uv at the XDG venv"
        echo "UV_PROJECT_ENVIRONMENT=\"$XDG_VENV_DIR\""
    } >> "$REPO_ROOT/.env"
    chmod 600 "$REPO_ROOT/.env"
    success ".env updated with UV_PROJECT_ENVIRONMENT"
fi

# ==============================================================================
# 7. Verification & Smoke Test
# ==============================================================================
header "7. Verifying Installation"

if [[ -x "$CLI_EXEC" ]]; then
    if "$CLI_EXEC" --help >/dev/null 2>&1; then
        success "vision-arwaky-cli runs and is ready to use!"
    else
        error "CLI execution check returned an unexpected status."
        exit 1
    fi
else
    error "vision-arwaky-cli binary was not found at $CLI_EXEC"
    exit 1
fi

# ==============================================================================
# Summary
# ==============================================================================
printf "\n%s%s========================================================================%s\n" "$BOLD" "$GREEN" "$RESET"
printf "%s%s[✓] Vision Arwaky installation complete! (100%% XDG Compliant)%s\n" "$BOLD" "$GREEN" "$RESET"
printf "%s%s========================================================================%s\n\n" "$BOLD" "$GREEN" "$RESET"

echo "XDG Directory Layout:"
echo "  - Venv & Data: $XDG_VENV_DIR"
echo "  - Binaries   : $BIN_DIR"
echo "  - Config     : $XDG_CONFIG_DIR"
echo "  - Cache      : $XDG_CACHE_DIR"
echo "  - Logs/State : $XDG_STATE_DIR"
echo ""
echo "CLI Commands:"
echo "  - vision-arwaky-cli   : Command line image & video analysis tool"
echo "  - vision-arwaky-mcp   : FastMCP server over stdio"
echo "  - vision-arwaky-tui   : Interactive Textual configuration UI"
echo ""
echo "Quick Test / Examples:"
echo "  1) Initialize any workspace:"
echo "     vision-arwaky-cli init /path/to/project"
echo ""
echo "  2) Analyze an image with AI vision:"
echo "     vision-arwaky-cli image photo.png"
echo ""
echo "  3) Analyze video frames and synthesize a summary:"
echo "     vision-arwaky-cli video recording.mp4"
echo ""
