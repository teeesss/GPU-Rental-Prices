# Project Intelligence: GPU Rental Index

## 📐 UI/UX Standards (V4.2.8+)

### Desktop Strategy
- **Base Font Size**: `14px` (`body`).
- **Data Table Fonts**: `11px` for GPU rows.
- **Layout**: Flexible grid with specific focus on readability.
- **Sidebar**: Standard `340px` fixed width.
- **Charts**: 5-day SMA smoothing; Logarithmic Y-axis to maintain H100 vs GB200 visibility.

### Mobile Strategy (Prioritize Density)
- **High-Density Grid**: `1.2fr 1fr 1fr 1fr 1.5fr` layout to fit 5 columns.
- **Alignment**: 
    - MODEL: Left
    - AVG: Center
    - CHG 1M: Center
    - CHG 1Y: Center
    - RANGE: Right
- **Vertical Rhythm**: `8px` row padding for "breathing room" in dense lists.
- **Navigation**: Eliminates non-essential labels to fit Chart + Market stats in one viewport.

### Column Definitions
1. **MODEL**: Canonical GPU name (e.g., H100).
2. **AVG**: 50/50 Weighted Index (Institutional Index + Market Median).
3. **CHG 1M**: % Change from 30 days ago (fallback to earliest record).
4. **CHG 1Y**: % Change from 365 days ago (fallback to earliest record).
5. **RANGE**: High/Low delta across all verified sources.

---

## ⚙️ Data Pipeline Logic

### Weighted Pricing (50/50 Model)
- **Institutional Index**: Scraped from ComputePulse.net.
- **Market Median**: Scraped from Vast.ai, RunPod, Nebius, and GetDeploying.
- **Formula**: `(Inst_Avg * 0.5) + (Market_Median * 0.5)`.
- **Fallback**: If one side is missing, the other takes 100% weight.

### Outlier & Sparse Data Protection
- **3-Source Minimum**: If market sources < 3, inject **Verified Benchmarks**.
- **25% Variance Gate**: Benchmarks only injected if within 25% of current market median.
- **Refresh Frequency**: 2 days (Matches observed market volatility).

### Change Calculations
- **Lookback Periods**: 30 days (1M), 365 days (1Y).
- **Fallback Logic**: If historical data is missing for the exact target date, the engine selects the **earliest available record** for that GPU.
- **Formatting**: Always include `+` or `-` sign with 1-decimal precision.

---

## 🚀 Deployment Rules
- **Production File**: `web/index.html` (Optimized for Mobile/Prod).
- **Sync Destination**: SFTP to `bmwseals.com/gpus/index.html`.
- **Development/Legacy**: `index_graph.html` (Used for local verification).
- **Data Bridge**: `database/gpu_intel.js` (Stats) and `database/gpu_history.js` (Time-series).

---

## 🛠️ Tech Stack
- **Frontend**: Vanilla HTML/JS, Chart.js, Luxon.
- **Backend**: Python 3.12, SQLite, Playwright.
- **Automation**: `gpu_pulse.py` (Orchestrator) & Cron.
