#!/bin/bash
# ============================================================================
#  GPU Neocloud Intel — Pulse Runner  (hardened, portable)
#  Fixes: apt atomic failure, t64 ABI, libu2f-udev removal, CIFS venv,
#         missing pip, Chromium shared-lib errors, cryptic tracebacks.
# ============================================================================
set -euo pipefail

# ── Banner ───────────────────────────────────────────────────────────────────
echo "============================================================"
echo "  GPU NEOCLOUD INTEL — PULSE RUNNER"
echo "============================================================"

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# ── Load environment ─────────────────────────────────────────────────────────
if [ -f ".env" ]; then
    set -a; . .env; set +a
fi

# ── Detect whether we can sudo non-interactively ─────────────────────────────
SUDO=""
if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
elif sudo -n true 2>/dev/null; then
    SUDO="sudo"
elif [ -t 0 ]; then
    SUDO="sudo"   # interactive terminal — prompt is fine
else
    SUDO=""
    echo "[!] No passwordless sudo and no TTY — skipping system package installs."
fi

# ── 1. Ensure python3 exists ─────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "[*] python3 not found — installing..."
    if [ -n "$SUDO" ]; then
        $SUDO apt-get update -y
        $SUDO apt-get install -y python3 python3-venv python3-pip python3-full
    else
        echo "[!] Cannot install python3 without sudo. Aborting." >&2
        exit 1
    fi
fi

# ── 2. System prerequisites ──────────────────────────────────────────────────
# FIX: install each package individually so one bad name cannot abort the batch.
# FIX: try t64 name first, then unversioned, so we work on jammy AND noble/resolute.
# FIX: libu2f-udev removed (does not exist on resolute).

BASE_PKGS=(
    python3 python3-venv python3-pip python3-full
    libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3
    libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libnss3 libnspr4
    libx11-6 libx11-xcb1 libxcb1 libxext6 libxi6 libxtst6
    fonts-liberation libvulkan1
)
# Packages that were renamed in the t64 ABI transition (24.04+).
# Order matters: try the modern name first, fall back to the legacy name.
T64_GROUPS=(
    "libatk1.0-0t64:libatk1.0-0"
    "libatk-bridge2.0-0t64:libatk-bridge2.0-0"
    "libcups2t64:libcups2"
    "libasound2t64:libasound2"
)

install_one() {
    # Try to install a single package; return 0 on success, 1 on failure.
    local pkg="$1"
    [ -n "$SUDO" ] || return 1
    $SUDO apt-get install -y --no-install-recommends "$pkg" &>/dev/null
}

pkg_installed() {
    dpkg -s "$1" &>/dev/null
}

echo "[*] Ensuring system prerequisites (python + browser libs)..."

# 2a. Refresh apt lists once (cheap, idempotent).
if [ -n "$SUDO" ]; then
    $SUDO apt-get update -y &>/dev/null || true
fi

# 2b. Install base packages one at a time.
MISSING_BASE=()
for pkg in "${BASE_PKGS[@]}"; do
    pkg_installed "$pkg" || MISSING_BASE+=("$pkg")
done

if (( ${#MISSING_BASE[@]} )); then
    echo "[*] Installing ${#MISSING_BASE[@]} missing base package(s)..."
    FAILED=()
    for pkg in "${MISSING_BASE[@]}"; do
        if install_one "$pkg"; then
            echo "    [ok]   $pkg"
        else
            echo "    [skip] $pkg  (unavailable on this release)"
            FAILED+=("$pkg")
        fi
    done
    (( ${#FAILED[@]} )) && echo "[!] Skipped: ${FAILED[*]}  (usually harmless)"
else
    echo "[*] Base prerequisites present."
fi

# 2c. Install t64-or-legacy groups.
for group in "${T64_GROUPS[@]}"; do
    modern="${group%%:*}"
    legacy="${group##*:}"
    if pkg_installed "$modern" || pkg_installed "$legacy"; then
        continue
    fi
    if install_one "$modern"; then
        echo "    [ok]   $modern"
    elif install_one "$legacy"; then
        echo "    [ok]   $legacy"
    else
        echo "    [skip] $modern / $legacy  (unavailable)"
    fi
done

# ── 3. Venv setup ────────────────────────────────────────────────────────────
# FIX: A venv is only valid if BOTH python AND pip work.
# FIX: Prefer $HOME when project dir is on a non-local FS (CIFS/NFS can't symlink).

VENV_FALLBACK="$HOME/.venv_gpu_intel"
PROJECT_VENV="$DIR/venv"

is_local_fs() {
    local fs
    fs=$(df --output=fstype "$1" 2>/dev/null | tail -1)
    case "$fs" in
        ext4|ext3|ext2|xfs|btrfs|zfs|f2fs|tmpfs|overlay) return 0 ;;
        *) return 1 ;;
    esac
}

if is_local_fs "$DIR"; then
    VENV_PATH="$PROJECT_VENV"
else
    fsname=$(df --output=fstype "$DIR" 2>/dev/null | tail -1)
    echo "[*] Project dir is on non-local FS ($fsname) — using $VENV_FALLBACK"
    VENV_PATH="$VENV_FALLBACK"
fi

venv_ok() {
    local v="$1"
    [ -x "$v/bin/python" ] || return 1
    "$v/bin/python" -c "import pip, venv" &>/dev/null || return 1
    return 0
}

if ! venv_ok "$VENV_PATH"; then
    echo "[*] (Re)creating virtual environment at $VENV_PATH ..."
    rm -rf "$VENV_PATH"
    mkdir -p "$(dirname "$VENV_PATH")"
    if ! python3 -m venv "$VENV_PATH" 2>/dev/null; then
        echo "[!] venv creation failed at $VENV_PATH — trying $VENV_FALLBACK"
        VENV_PATH="$VENV_FALLBACK"
        rm -rf "$VENV_PATH"
        mkdir -p "$VENV_PATH"
        python3 -m venv "$VENV_PATH"
    fi
    # Bootstrap pip if ensurepip was stripped from the base image.
    if ! "$VENV_PATH/bin/python" -c "import pip" &>/dev/null; then
        echo "[*] Bootstrapping pip into venv..."
        "$VENV_PATH/bin/python" -m ensurepip --upgrade \
          || curl -sS https://bootstrap.pypa.io/get-pip.py | "$VENV_PATH/bin/python"
    fi
fi

VENV_PYTHON="$VENV_PATH/bin/python"
echo "[*] Using venv: $VENV_PATH"

# ── 4. Python dependencies ───────────────────────────────────────────────────
if [ -f "requirements.txt" ]; then
    echo "[*] Installing Python dependencies..."
    "$VENV_PYTHON" -m pip install --upgrade pip wheel --quiet
    "$VENV_PYTHON" -m pip install --no-input --no-warn-script-location \
        -r requirements.txt --quiet
fi

# ── 5. Playwright browser + OS deps ──────────────────────────────────────────
# FIX: This is what was missing. install-deps pulls the libatk/libnss/etc.
#      packages Chromium actually needs; install chromium fetches the binary.
if grep -qi "playwright" requirements.txt 2>/dev/null; then
    echo "[*] Ensuring Playwright Chromium + system deps..."
    if [ -n "$SUDO" ]; then
        # Official, distro-aware path. Handles t64 renames automatically.
        if ! $SUDO "$VENV_PYTHON" -m playwright install-deps chromium; then
            echo "[!] playwright install-deps failed — continuing (manual libs may suffice)."
        fi
    else
        echo "[!] No sudo — skipping playwright install-deps."
        echo "    If Chromium fails to launch, run:"
        echo "      sudo $VENV_PYTHON -m playwright install-deps chromium"
    fi
    "$VENV_PYTHON" -m playwright install chromium
fi

# ── 6. Chromium smoke test ───────────────────────────────────────────────────
# FIX: Fail fast with a clear message instead of a cryptic async traceback.
if grep -qi "playwright" requirements.txt 2>/dev/null; then
    echo "[*] Chromium smoke test..."
    if ! "$VENV_PYTHON" - <<'PY' &>/dev/null
import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(headless=True)
        await b.close()
asyncio.run(main())
PY
    then
        echo "[!] Chromium smoke test FAILED." >&2
        echo "    Diagnose with:" >&2
        echo "      ldd ~/.cache/ms-playwright/chromium*/chrome-linux/chrome | grep 'not found'" >&2
        echo "      sudo $VENV_PYTHON -m playwright install-deps chromium" >&2
        exit 1
    fi
    echo "[*] Chromium smoke test: OK"
fi

# ── 7. Run the pulse pipeline ────────────────────────────────────────────────
mkdir -p "$DIR/logs"
LOG="$DIR/logs/gpu_pulse.log"
export GPU_DB_PATH="${GPU_DB_PATH:-$HOME/gpu_intel_temp.db}"

echo "[*] Running GPU pulse pipeline..."
"$VENV_PYTHON" gpu_pulse.py "$@" 2>&1 | tee -a "$LOG"

echo "============================================================"
echo "  DONE — Live: https://bmwseals.com/gpus/"
echo "============================================================"
