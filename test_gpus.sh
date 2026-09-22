#!/bin/bash
# ============================================================================
# GPU Neocloud Intel — Dry Run Tester
# Runs the scraper in dry-run mode (no SQLite writes)
# ============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Load Environment Variables (.env Portability)
if [ -f ".env" ]; then
    set -a
    . .env
    set +a
fi

# ── 1. Venv & Dependencies Setup ───────────────────────────────────────────────
VENV_PATH="./venv"
VENV_FALLBACK="$HOME/.venv_gpu_intel"

# Check if current venv is missing or non-functional (catches broken mount symlinks)
if ! "$VENV_PATH/bin/python" --version &>/dev/null 2>&1 && ! "$VENV_FALLBACK/bin/python" --version &>/dev/null 2>&1; then
    echo "[*] Creating virtual environment for tests..."
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
        VENV_PATH="$VENV_FALLBACK"
        VENV_PYTHON="$VENV_PATH/bin/python"
    else
        echo "[!] Could not find a working venv python. Exiting."
        exit 1
    fi
fi


if [ -f "requirements.txt" ]; then
    echo "[*] Checking dependencies..."
    "$VENV_PYTHON" -m pip install --upgrade pip --quiet
    "$VENV_PYTHON" -m pip install --no-input --no-warn-script-location -r requirements.txt --quiet
    if grep -qi "playwright" requirements.txt; then
        if ! "$VENV_PYTHON" -m playwright install chromium --dry-run &>/dev/null; then
            echo "[*] Installing Playwright Chromium for tests..."
            "$VENV_PYTHON" -m playwright install chromium &>/dev/null
        fi
    fi
fi

# ── 2. Run Test ──────────────────────────────────────────────────────────────
echo "[*] Running scraper diagnostic test (DRY RUN)..."
"$VENV_PYTHON" engine/test_scraper.py

echo ""
echo "[*] Diagnostic complete."
