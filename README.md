# GPU Price Over Time — V4.2.6

**Sovereign Neocloud Intelligence Engine**

Tracks and visualizes GPU rental prices across AI Neoclouds, cloud marketplaces, and institutional indices. Renders a live dashboard at [bmwseals.com/gpus](https://bmwseals.com/gpus/).

---

## Architecture: The 50/50 Weighted Engine

The V4.2.1 engine implements an institutional-grade pricing model to ensure data stability and accuracy:

1. **Market Intelligence**: Real-time scraper pulls from GetDeploying, Vast.ai, RunPod, and Nebius.
2. **Institutional Index**: Automated anchor pull from ComputePulse.net.
3. **Synthetic Verification**: Ensures a minimum of 3 sources per GPU by injecting verified benchmarks (filtered by a 25% variance guardrail).
4. **Weighted Averaging**: Calculates a final "Truth" price using a 50/50 split between Market Medians and Institutional Indices.
5. **Mobile-First UX**: High-density 9-column single-line ticker and vertical compression for vertical viewport situational awareness.

---

## Production Pipeline

### Manual Run
```bash
./gpu.sh
```

### Cron Job (Linux)
Recommended: Every 2 days at 6am.
```bash
0 6 */2 * * cd /path/to/GPU_Price_Over_Time && ./gpu.sh >> logs/cron.log 2>&1
```

### Windows Task Scheduler
Create a task to run `python.exe gpu_pulse.py` every 2 days at 6am.

---

## Files Reference

| File | Purpose |
|---|---|
| `gpu_pulse.py` | Primary entry point (Staleness-gated) |
| `engine/scraper.py` | Phase 1: All live scrapers & Institutional pull |
| `engine/build_intel.py` | Phase 2: Weighted aggregation & Synthetic verification |
| `engine/remote_sync.py` | Phase 3: Secure SFTP deployment |
| `web/index.html` | Dashboard (Chart.js V4 + Luxon) |
| `database/gpu_intel.db` | SQLite Historical Vault |
| `database/gpu_history.js` | Time-series data bridge |
| `database/gpu_intel.js` | Summary & Stats data bridge |
