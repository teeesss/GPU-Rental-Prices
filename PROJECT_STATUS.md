# PROJECT STATUS

## Current Status
- **V4.2.31 Live** at https://bmwseals.com/gpus
- **YTD Column Integration**: Calculated YTD percentage price change on backend (since January 1st), widened desktop/tablet sidebar layout to move graph leftwards, aligned table header fonts to `#ccc`, centered RANGE header, and removed +/- sign indicators to maximize space and look crisper.
- **1W Price Changes & Column Alignment**: Added 7-day price lookbacks on backend, rendered 1W percentage change column, renamed W. AVG to AVG, and aligned CSS grid layout for seamless desktop and mobile viewports.
- **Venv & Stealth Reliability**: Synced requirements, resolved playwright_stealth ImportError by adopting object-oriented API, and enabled fallback venv reuse.
- **Mobile Grid & Responsive Sync Indicators**: Active; engineered separated date/elapsed sub-labels in stat-cards with CSS hides to avoid narrow overflow on mobile, and implemented a premium bordered card layout for mobile viewports.
- **Outlier Shield**: Median-based outlier detection active; automatically discards market price aberrations deviating >35% from the median.
- **Label & Date Calibration**: Pricing timestamps added to cards and header; headers realigned to resolve visual ambiguity.
- **Reliability Lockdown**: Database migrated to native ext4 FS (`$HOME/gpu_intel.db`); WAL mode active.
- **Scraper Hardening**: ComputePulse email wall bypass fully automated.
- **Visual Hardening**: GPU Labels calibrated to 27px Desktop focus.
- **Color Synchronization**: UI chips match model-specific chart palettes.
- Institutional-grade **50/50 Weighted Pricing Engine** operational.
- Autonomous refresh pipeline running every 2 days via `gpu.sh`.
 
## Recent Milestones
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
