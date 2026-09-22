# TEST GUIDE — GPU Intelligence Engine

## Overview
This guide covers how to verify the integrity of the GPU price intelligence pipeline.

## 🧪 Smoke Tests
The primary health check is `smoke_test.py`. It verifies:
1. `database/gpu_history.json` exists and is readable.
2. Data entries are not empty.
3. The latest batch contains price points for all priority models.

### Run Smoke Test
```bash
python smoke_test.py
```

## 🧩 Scraper Unit Tests
To verify GetDeploying DOM parsing accuracy against modern HTML layouts without launching browsers:
```bash
python engine/test_getdeploying_parser.py
```

## 🛠️ Diagnostic Tools
Several scratch scripts are available for deep diagnostics:
- `scratch/diag_db.py`: Inspects the SQLite database integrity.
- `scratch/align_ts.py`: Checks for timestamp synchronization across sources.
- `engine/backfill_bridge.py`: Diagnostic and gap recovery tool for multi-day staleness.

## 📡 Scraper Dry-Runs
To test the scrapers without writing to the production database, use the `test_gpus.sh` script:
```bash
./test_gpus.sh
```
This script will:
1. Initialize a temporary venv.
2. Run `engine/test_scraper.py`.
3. Report live data points without modifying `~/gpu_intel.db`.

## 🔒 Locking & Concurrency Tests
If you encounter "database is locked" errors:
1. Ensure `GPU_DB_PATH` is pointing to a native Linux filesystem (ext4).
2. Run `python scratch/diag_db.py` to check for WAL journal status.

---
Updates to test results are recorded in [TEST_RESULTS.md](TEST_RESULTS.md).
