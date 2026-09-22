# Neocloud GPU Intelligence Engine (V4.2.33)

> Institutional-grade GPU rental price tracking and autonomous market intelligence.

[![Live Dashboard](https://img.shields.io/badge/Live-bmwseals.com/gpus-green?style=for-the-badge)](https://bmwseals.com/gpus/)

---

## 🚀 Overview
The **Sovereign Neocloud Intelligence Engine** is a robust pipeline for tracking, analyzing, and visualizing GPU rental prices across the global Neocloud market. It bridges the gap between institutional indices and retail marketplace pricing through a weighted intelligence model.

### Key Features
- **Weighted Intelligence**: 50/50 model balancing Institutional Indices (ComputePulse) vs. Marketplace Realities.
- **Autonomous Pipeline**: Scrape → Build → Sync cycle with 2-day staleness gating.
- **Resilient Architecture**: Local filesystem temp-scraping & single-transaction merge for 100% reliable SQLite locking across network mounts.
- **Stealth Browsing**: V28 Stealth Navigator bypassing 2026-grade bot detection.
- **Universal Design**: Multi-tier vertical scaling and color-synchronized UI elements.

---

## 🛠️ Tech Stack
- **Engine**: Python 3.12+ (Playwright, SQLite3, Paramiko)
- **Frontend**: Vanilla HTML5, CSS3 (Glassmorphism), Chart.js (Luxon Adapter)
- **Infrastructure**: WSL2/Linux (ext4), SFTP Production Sync
- **Design**: "Antigravity" Design System (27px Desktop Focus)

---

## ⚙️ Usage

### Quick Start
```bash
./gpu.sh         # Runs ingestion + build + deploy (if data > 2 days old)
./gpu1.sh        # Hardened portable runner for Ubuntu 24.04+/t64 & CIFS mounts
./gpu.sh --force # Force an immediate production update
./gpu.sh --check # Just check the current data age
```

### Manual Controls
```bash
python gpu_pulse.py --check              # Check status without shell wrapper
python engine/scraper.py                 # Run ingestion only
python engine/build_intel.py             # Rebuild JS artifacts from DB
python engine/remote_sync.py             # Sync to production manually
```

---

## 📐 Architecture
- **Ingestion**: `engine/scraper.py` orchestrates multi-source scraping (GetDeploying, Vast, RunPod, Nebius).
- **Institutional Data**: `engine/index_scraper.py` handles ComputePulse (includes automated email wall bypass).
- **Intelligence Bridge**: `engine/build_intel.py` aggregates data, applies weights, and generates `database/gpu_intel.js`.
- **Persistence**: `~/gpu_intel_temp.db` (Local ext4 temp DB) for scraping; merged into `database/gpu_intel.db` (Workspace DB) for persistence.
- **Stealth**: `engine/stealth_navigator.py` provides Chrome-grade fingerprinting.

---

## 🔧 Environment Setup
Copy `.env.example` to `.env` and configure:
```ini
SFTP_HOST=bmwseals.com
SFTP_USER=...
SFTP_PASS=...
SFTP_PATH=/path/to/public_html/gpus
```

### Prerequisites
- Python 3.12+
- `pip install -r requirements.txt`
- `playwright install chromium`

---

## 🧪 Testing
Run the smoke test to verify database and artifact integrity:
```bash
python smoke_test.py
```
Refer to [TEST_GUIDE.md](file:///z:/GPU_Price_Over_Time/TEST_GUIDE.md) for more details.

---

## 📜 Version History
- **V4.2.33**: GB200 Calibration, Aug-Sept Gap Backfill & AMD MI300X Integration. Decoupled GB200 from ComputePulse B200 false-matches (~$17.27/hr), bridged the 38-day gap with 18 2-day cadence snapshots, and replaced MI325X/MI355X with AMD MI300X across scrapers and 8-column UI.
- **V4.2.32**: GetDeploying Scraper Overhaul & Portable Runner. Upgraded GetDeploying extractor for 2026 UI overhaul and added `gpu1.sh` hardened runner for Ubuntu 24.04+ (t64 package management & CIFS venv fallback).
- **V4.2.31**: YTD Column Integration. Added Year-to-Date (YTD) price changes, widened sidebar layout on desktop/tablet, aligned column headers to `#ccc` font color, and centered the RANGE header.
- **V4.2.30**: 1W Change & Evasion Hardening. Added 1-week price changes (1W), changed W. AVG to AVG, unified playwright-stealth to 2.0.3, and migrated to temp-scrape-and-merge DB pattern.
- **V4.2.26**: Reliability Hardening. Native FS migration & ComputePulse email bypass.
- **V4.2.25**: Color-Synchronized Filters.
- **V4.2.23**: Universal Responsive Tiering.
- **V4.2.1**: GA Release with Institutional Weights.

---
© 2026 Sovereign Neocloud Intelligence. All rights reserved.
