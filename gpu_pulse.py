#!/usr/bin/env python3
"""
gpu_pulse.py  —  One-command GPU intelligence update.

Usage:
    python gpu_pulse.py             # run if data is stale (>2 days old)
    python gpu_pulse.py --force     # always run regardless of age
    python gpu_pulse.py --check     # just report current data age, don't run

Cron (Linux):
    Every 2 days at 6am:
        0 6 */2 * * cd /path/to/GPU_Price_Over_Time && ./gpu.sh >> logs/cron.log 2>&1
"""

import sys
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT   = Path(__file__).parent
DB     = ROOT / "database" / "gpu_intel.db"
LOGS   = ROOT / "logs"
LOGS.mkdir(exist_ok=True)

# ── Config ──────────────────────────────────────────────────────────────────────
STALE_AFTER_DAYS = 2.0   # Matches market volatility (changes every 2-3 days)


def data_age() -> float | None:
    """Return age of most recent DB record in days, or None if DB is empty."""
    if not DB.exists():
        return None
    conn = sqlite3.connect(DB)
    row = conn.execute("SELECT MAX(timestamp) FROM prices").fetchone()
    conn.close()
    if not row or not row[0]:
        return None
    try:
        last = datetime.fromisoformat(row[0].replace("Z", "+00:00"))
    except:
        return 999.0 # Force update on parse error
    return (datetime.now(timezone.utc) - last).total_seconds() / 86400


def run_step(label: str, cmd: list[str]) -> bool:
    print(f"\n  [{label}]")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        print(f"  !! {label} FAILED (exit {result.returncode})")
        return False
    return True


def main():
    force = "--force" in sys.argv
    check = "--check" in sys.argv

    age = data_age()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    print(f"\n{'='*55}")
    print(f"  GPU NEOCLOUD INTEL — PULSE RUNNER  [{now_str}]")
    print(f"{'='*55}")

    if age is None:
        print("  Status : No data found — running initial ingestion")
    else:
        print(f"  Last pulse : {age:.2f} days ago")
        print(f"  Stale after: {STALE_AFTER_DAYS} days")

    if check:
        if age is not None:
            status = "FRESH" if age < STALE_AFTER_DAYS else "STALE"
            print(f"  Data status: {status}")
        sys.exit(0)

    if not force and age is not None and age < STALE_AFTER_DAYS:
        print(f"\n  Data is fresh ({age:.2f}d old). Skipping.")
        print(f"  Use --force to override.\n")
        sys.exit(0)

    print("\n  Starting intelligence pipeline...\n")

    steps = [
        ("Full Intelligence Pipeline", ["python", "engine/scraper.py"]),
    ]

    for label, cmd in steps:
        ok = run_step(label, cmd)
        if not ok:
            print("\n  Pipeline aborted.\n")
            sys.exit(1)

    print("\n  Pipeline complete. Live at: https://bmwseals.com/gpus/\n")


if __name__ == "__main__":
    main()
