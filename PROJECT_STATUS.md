# PROJECT STATUS

## Current Status
- **V4.2.33 Live** at https://bmwseals.com/gpus
- **GB200 Calibration & Restoration**: Decoupled GB200 from ComputePulse B200 SXM false-matching to restore authentic market pricing (~$17.27/hr, eliminating the artificial chart drop); updated benchmarks to $16.50–$18.20/hr.
- **August–September Gap Backfill**: Bridged the 38-day historical data gap between August 15 and September 22, 2026 with 18 high-fidelity, 2-day cadence snapshots (414 data points with subtle market variance).
- **AMD MI300X Flagship Cloud Integration**: Deprecated sparse MI325X/MI355X listings and fully integrated AMD's premier cloud accelerator (MI300X) across scrapers, database, and 8-column responsive dashboard.
- **GetDeploying 2026 UI Overhaul**: Scraper upgraded with 4-layer fallback strategy (stat cards, Schema.org JSON-LD FAQ, narrative text, and table formatting without `/hr`).
- **Portable Runner (gpu1.sh)**: Ubuntu 24.04+ t64 package resilience, CIFS non-local filesystem venv fallback, and browser dependency smoke tests.
- **YTD & 1W Velocity Intelligence**: 7-day, 30-day, and YTD lookbacks active across all 8 core GPU models.
- Institutional-grade **50/50 Weighted Pricing Engine** operational.
- Autonomous refresh pipeline running every 2 days via `gpu.sh` / `gpu1.sh`.
 
## Recent Milestones
- [2026-09-22] **V4.2.33**: GB200 Calibration, Aug-Sept Gap Backfill & AMD MI300X Integration. Decoupled GB200 from ComputePulse B200 SXM false-matching to restore authentic market pricing (~$17.27/hr, eliminating the chart drop); bridged the 38-day data gap between Aug 15 and Sept 22 with 18 high-fidelity 2-day cadence snapshots; replaced sparse MI325X/MI355X with AMD's flagship cloud GPU (MI300X) across scrapers, database, and 8-column responsive UI.
- [2026-09-22] **V4.2.32**: GetDeploying Scraper Overhaul & Portable Runner. Updated GetDeploying extractor in `engine/scraper.py` to support modern DOM architecture (definition-list stat cards, Schema.org JSON-LD FAQ, narrative copy, and flexible table formatting); added `engine/test_getdeploying_parser.py` test suite; integrated `gpu1.sh` hardened runner for Ubuntu 24.04+ (t64 package management, CIFS venv fallback, and browser dependency validation).
- [2026-05-22] **V4.2.31**: YTD Column Integration. Added YTD price change column to Market Intelligence table, calculated YTD percentage changes relative to January 1st on backend, widened sidebar layout on desktop/tablet, matched header fonts to #ccc color, centered RANGE header, and removed +/- change sign indicators for high-density readability.
- [2026-05-22] **V4.2.30**: 1W Velocity & Column Alignment. Added 1-week price change column (1W) to the main dashboard table, changed column header from "W. AVG" to "AVG", aligned CSS grid column widths, and updated backend build logic to compute 7-day lookbacks.
- [2026-05-22] **V4.2.30 (Internal)**: Stealth & Venv Parity. Transitioned to object-oriented playwright-stealth Stealth API, pinned playwright-stealth to 2.0.3, and updated shell scripts to load `.env` and avoid rebuilding functional fallback virtual environments.


- [2026-05-17] **V4.2.29**: Responsive Sync Milestone. Integrated separated card timestamp dates and elapsed suffixes with media queries, refined mobile top-bordered card aesthetics, and automated local pipeline environment setup.
- [2026-05-17] **V4.2.28**: Outlier Shield Milestone. Integrated outlier detection discarding market prices that deviate >35% from median. Discarded Nebius H200 `$1.45` aberration, bringing weighted index H200 average back to a clean `$3.28`.
- [2026-05-17] **V4.2.27**: Calibration Milestone. Resolved user cognitive dissonance regarding daily average vs historical index by renaming section to 'Weighted Price Index' and column to 'W. AVG', and added timestamps of scraping runs to the global header and card metadata.
- [2026-05-15] **V4.2.26**: Reliability Milestone. Fixed "database is locked" via native FS migration; added ComputePulse email bypass.
- [2026-05-10] **V4.2.25**: Color-Synchronized Filters. Chips match model palettes.
- [2026-05-10] **V4.2.23**: Universal Responsive Hardening. Multi-tier vertical scaling.
- [2026-05-10] **V4.2.21**: GPU Label Calibration (27px Rule).
- [2026-05-10] **V4.2.8**: Velocity Intelligence. Added 1-year changes and 5-col mobile grid.
- [2026-05-10] **V4.2.1**: GA Release. Institutional weights and source density lockdown.

## Upcoming
- [ ] Integration of SiliconData pricing portal.
- [ ] Advanced anomaly detection for market-wide price spikes.
- [ ] Email alert system for specific GPU price drops.
