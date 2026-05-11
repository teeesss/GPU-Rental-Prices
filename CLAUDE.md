# CLAUDE.md — GPU Price Over Time

## Project
**Sovereign Neocloud Intelligence Engine V4.2.1**
Live at: https://bmwseals.com/gpus/

## Architecture Summary
- **Scraper**: `engine/scraper.py` — async Playwright (StealthNavigator). Sources: GetDeploying, Vast.ai, RunPod, Nebius.
- **Institutional Index**: `engine/index_scraper.py` — Pulls from ComputePulse.net.
- **Weighted Engine**: `engine/build_intel.py` — Calculates 50/50 Weighted Average (Institutional vs Market).
- **Synthetic Verification**: Ensures a **3-source minimum** per GPU by injecting verified benchmarks if market data is sparse.
- **Outlier Protection**: Implements a **25% variance gate** to reject anomalies (e.g. $18.22/hr GB200).
- **Pipeline Runner**: `gpu_pulse.py` — 2-day staleness gate, `--force`/`--check` flags.
- **Deploy**: `engine/remote_sync.py` — SFTP to bmwseals.com.

## Key Commands
```bash
./gpu.sh                     # Primary entry point (Staleness-gated)
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

## Documentation Rules
- Refer to `knowledge.md` for UI/UX standards (Desktop vs Mobile).
- Keep `web/index.html` as the production source of truth.
- Update `TASKS.md` after logic changes.


