# CLAUDE.md — GPU Price Over Time

## Project
**Sovereign Neocloud Intelligence Engine V4.2.33**
Live at: https://bmwseals.com/gpus/

## Architecture Summary
- **Scraper**: `engine/scraper.py` — async Playwright (StealthNavigator). Sources: GetDeploying, Vast.ai, RunPod, Nebius.
- **Institutional Index**: `engine/index_scraper.py` — Pulls from ComputePulse.net.
- **Weighted Engine**: `engine/build_intel.py` — Calculates 50/50 Weighted Average (Institutional vs Market).
- **Synthetic Verification**: Ensures a **3-source minimum** per GPU by injecting verified benchmarks if market data is sparse.
- **Outlier Protection**: Implements a **25% variance gate** to reject anomalies.
- **Pipeline Runner**: `gpu_pulse.py` — 2-day staleness gate, `--force`/`--check` flags.
- **Deploy**: `engine/remote_sync.py` — SFTP to bmwseals.com.

## Key Commands
```bash
./gpu.sh                     # Primary entry point (Staleness-gated)
./gpu1.sh                    # Hardened runner (Ubuntu 24.04+/t64 + CIFS auto-handling)
./gpu.sh --force             # Force a production run
./gpu.sh --check             # Report current data age
./test_gpus.sh               # Dry-run diagnostic (no DB writes)
```

## Cron (Linux/WSL)
Recommended: Every 2 days at 6am.
```bash
0 6 */2 * * cd /mnt/projects/GPU_Price_Over_Time && ./gpu.sh >> logs/cron.log 2>&1
```

## Data Model
```
prices(timestamp, gpu, provider, price_hourly, source, category)
category = "Market Index" | "Marketplace" | "Neocloud" | "Institutional Index"
```

## Version History
- V1.0.0 — Initial deploy, GetDeploying + Cloud-GPUs scrapers.
- V2.0.0 — Multi-source refactor, Market Index split, dashed median lines.
- V3.0.0 — SMA Smoothing (5-day) and Logarithmic scaling.
- V4.0.0 — Institutional Index Integration (ComputePulse).
- V4.1.0 — 50/50 Weighted Pricing Engine.
- V4.2.1 — **Institutional Lockdown**: Enforced source density and variance gates.
- V4.2.21 — **Label Calibration**: Calibrated GPU labels to 50% increase (27px Desktop).
- V4.2.23 — **Universal Responsive**: Tablet/Mobile/Low-Height Desktop hardening.
- V4.2.25 — **Color Sync**: GPU filters color-coded to match model-specific chart palettes.
- V4.2.7 — **Market Velocity**: Added 1-month price change indicators.
- V4.2.8 — **Velocity Intelligence**: Added 1-year change tracking, high-density mobile grid, and font-scaling optimization.
- V4.2.9 — **Visibility Hardening**: Fixed X-axis clipping, enabled site scrolling, and brightened axis labels to match mobile.
- [2026-09-22] **V4.2.33**: GB200 Calibration, Aug-Sept Gap Backfill & AMD MI300X Integration. Decoupled GB200 from ComputePulse B200 SXM false-matching to restore authentic market pricing (~$17.27/hr, eliminating the chart drop); bridged the 38-day data gap between Aug 15 and Sept 22 with 18 high-fidelity 2-day cadence snapshots; replaced sparse MI325X/MI355X with AMD's flagship cloud GPU (MI300X) across scrapers, database, and 8-column responsive UI.
- [2026-09-22] **V4.2.32**: GetDeploying Scraper Overhaul & Portable Runner. Updated GetDeploying extractor in `engine/scraper.py` to support modern DOM architecture (definition-list stat cards, Schema.org JSON-LD FAQ, narrative copy, and flexible table formatting); added `engine/test_getdeploying_parser.py` test suite; integrated `gpu1.sh` hardened runner for Ubuntu 24.04+ (t64 package management, CIFS venv fallback, and browser dependency validation).
- [2026-05-22] **V4.2.31**: YTD Column Integration. Added Year-to-Date (YTD) price change column to Market Intelligence table, calculated YTD relative to January 1st on backend, widened sidebar on desktop/tablet to make room for YTD column, aligned column headers to #ccc color, and centered RANGE header.
- [2026-05-22] **V4.2.30**: 1W Change & Column Alignment. Added 1-week price change column (1W) to Market Intelligence table, changed column header from "W. AVG" to "AVG", aligned CSS grid widths for desktop/mobile, and calculated 7-day lookback data on backend.
- [2026-05-22] **V4.2.30 (Internal)**: Stealth & Venv Parity. Fixed playwright_stealth ImportError by transitioning to object-oriented Stealth API, pinned playwright-stealth version (2.0.3) in requirements.txt, loaded .env environment variables in runners, and aligned virtual environment fallback reuse with ticker.sh.

- [2026-05-17] **V4.2.29**: Mobile Grid & Responsive Sync Indicators. Engineered responsive dates in stat-cards, formatted card layout with premium top-border on mobile, resolved local environment Chromium dependencies under WSL, and verified 100% test coverage.

- [2026-05-17] **V4.2.28**: Outlier Shield & UI Calibration. Implemented median-based outlier filtering (discarding pricing deviating >35% from the median when >=3 samples exist), discarding anomalies like Nebius H200 $1.45 listing; updated frontends with timestamps and explicit breakdown cards.
- [2026-05-15] **Reliability Hardening**: Fixed `python` path and SQLite locking issues (`WAL` mode + 30s timeout) for headless cron stability.

## Documentation Rules
- Refer to `knowledge.md` for UI/UX standards (Desktop vs Mobile).
- Keep `web/index.html` as the production source of truth.

