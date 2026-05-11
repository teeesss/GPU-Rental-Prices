#!/bin/bash
# ============================================================================
# GPU Neocloud Intel — Pulse Runner
# Full Cycle: Scrape → Build JS Bridge → Deploy to bmwseals.com/gpus
# Usage:
#   ./gpu.sh              # run if data is stale (>2 days)
#   ./gpu.sh --force      # always run
#   ./gpu.sh --check      # report data age only
# ============================================================================

set -e

echo "============================================================"
echo "  GPU NEOCLOUD INTEL — PULSE RUNNER"
echo "============================================================"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# ── 1. Python check ──────────────────────────────────────────────────────────
if ! command -v python3 &> /dev/null; then
    echo "[!] Python3 not found. Install python3 and retry."
    exit 1
fi

if ! python3 -c "import venv" &> /dev/null; then
    echo "[!] python3-venv missing."
    read -p "[?] Install via apt? (y/n): " confirm
    if [[ $confirm == [yY]* ]]; then
        sudo apt update -y &>/dev/null
        sudo apt install python3-venv python3-full -y
    else
        echo "[!] Cancelled. Exiting."
        exit 1
    fi
fi

# ── 2. Venv setup ────────────────────────────────────────────────────────────
VENV_PATH="./venv"
VENV_FALLBACK="$HOME/.venv_gpu_intel"

if ! "$VENV_PATH/bin/python" --version &>/dev/null 2>&1; then
    echo "[*] Creating virtual environment..."
    if ! python3 -m venv "$VENV_PATH" 2>/dev/null; then
        echo "[!] Failed to create venv here (mount issue?). Trying $VENV_FALLBACK..."
        mkdir -p "$VENV_FALLBACK"
        python3 -m venv "$VENV_FALLBACK"
        VENV_PATH="$VENV_FALLBACK"
    fi
fi

# Resolve final python path
VENV_PYTHON="$VENV_PATH/bin/python"
if ! "$VENV_PYTHON" --version &>/dev/null 2>&1; then
    if "$VENV_FALLBACK/bin/python" --version &>/dev/null 2>&1; then
        VENV_PYTHON="$VENV_FALLBACK/bin/python"
    else
        echo "[!] Could not find a working venv python. Exiting."
        exit 1
    fi
fi

# ── 3. Dependencies ──────────────────────────────────────────────────────────
if [ -f "requirements.txt" ]; then
    echo "[*] Checking dependencies..."
    "$VENV_PYTHON" -m pip install --upgrade pip --quiet
    "$VENV_PYTHON" -m pip install --no-input --no-warn-script-location \
        -r requirements.txt --quiet

    if grep -qi "playwright" requirements.txt; then
        echo "[*] Verifying Playwright..."
        if ! "$VENV_PYTHON" -m playwright install chromium --dry-run &>/dev/null; then
            echo "[*] Installing Playwright Chromium..."
            "$VENV_PYTHON" -m playwright install chromium &>/dev/null
        fi
    fi
fi

# ── 4. Run pulse ─────────────────────────────────────────────────────────────
mkdir -p "$DIR/logs"
LOG="$DIR/logs/gpu_pulse.log"

echo "[*] Running GPU pulse pipeline..."
"$VENV_PYTHON" gpu_pulse.py "$@" 2>&1 | tee -a "$LOG"

echo "============================================================"
echo "  DONE — Live: https://bmwseals.com/gpus/"
echo "============================================================"
