import sqlite3
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta, timezone
from scraper import VERIFIED_BENCHMARKS

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "database" / "gpu_intel.db"
BRIDGE_FILE = DB_PATH.parent / "gpu_intel.js"

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("build_intel")

def get_historical_avg(c, gpu, target_date_iso):
    """Calculate what the weighted average was at a specific historical timestamp."""
    c.execute("SELECT DISTINCT timestamp FROM prices WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1", (target_date_iso,))
    row = c.fetchone()
    if not row:
        # Fallback: Use the earliest available data if 30 days haven't passed
        c.execute("SELECT DISTINCT timestamp FROM prices ORDER BY timestamp ASC LIMIT 1")
        row = c.fetchone()
    
    if not row:
        return None
    ts = row[0]
    
    # Get Institutional Index for that TS
    c.execute("SELECT AVG(price_hourly) FROM prices WHERE timestamp = ? AND gpu = ? AND category = 'Institutional Index'", (ts, gpu))
    inst_price = c.fetchone()[0]
    
    # Get Market Average for that TS
    c.execute("SELECT AVG(price_hourly) FROM prices WHERE timestamp = ? AND gpu = ? AND category != 'Institutional Index'", (ts, gpu))
    market_price = c.fetchone()[0]
    
    if inst_price and market_price:
        return (inst_price * 0.5) + (market_price * 0.5)
    return inst_price or market_price

def build():
    if not DB_PATH.exists():
        log.error("Database missing.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # 0. Filter Whitelist
    TARGET_GPUS = ["H100", "H200", "B200", "GB200", "B300", "GH200", "MI325X", "MI355X", "A100"]

    # 1. Full History
    c.execute("SELECT * FROM prices ORDER BY timestamp ASC")
    all_history = [dict(row) for row in c.fetchall()]
    history = [h for h in all_history if h['gpu'] in TARGET_GPUS]
    log.info(f"Filtered {len(history)} historical records (from {len(all_history)} total).")
    
    # 2. Latest Snapshot (Robust)
    c.execute("SELECT MAX(timestamp) FROM prices")
    last_ts = c.fetchone()[0]
    log.info(f"Latest batch timestamp: {last_ts}")
    
    c.execute("SELECT * FROM prices WHERE timestamp = ?", (last_ts,))
    latest_raw = [dict(row) for row in c.fetchall() if row['gpu'] in TARGET_GPUS]
    
    # Enrich with source URLs
    latest = []
    for r in latest_raw:
        url = "N/A"
        if r['provider'] == 'GetDeploying':
            gpu_slug = r['gpu'].lower().replace(" ", "-")
            url = f"https://getdeploying.com/gpus/nvidia-{gpu_slug}"
        elif r['category'] == 'Institutional Index':
            url = f"https://www.computepulse.net/{r['gpu'].lower()}"
        
        r['source_url'] = url
        latest.append(r)
        
    log.info(f"Found {len(latest)} target records in the latest snapshot.")
    
    # 3. Aggregates with 50/50 Institutional Weighting
    c.execute("SELECT DISTINCT gpu FROM prices WHERE timestamp = ?", (last_ts,))
    all_gpus = [row[0] for row in c.fetchall() if row[0] in TARGET_GPUS]
    
    # Determine comparison dates
    try:
        now_dt = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
    except:
        now_dt = datetime.now(timezone.utc)
    month_ago_iso = (now_dt - timedelta(days=30)).isoformat()
    year_ago_iso  = (now_dt - timedelta(days=365)).isoformat()

    stats = []
    for gpu in all_gpus:
        # Get Institutional Index
        c.execute("""
            SELECT AVG(price_hourly) FROM prices 
            WHERE timestamp = ? AND gpu = ? AND category = 'Institutional Index'
        """, (last_ts, gpu))
        inst_price = c.fetchone()[0]
        
        c.execute("""
            SELECT price_hourly, category FROM prices 
            WHERE timestamp = ? AND gpu = ? AND category != 'Institutional Index'
        """, (last_ts, gpu))
        rows = c.fetchall()
        market_prices = [r[0] for r in rows]
        market_count = len(market_prices)
        
        # --- PHASE 2.5: Inject Verified Benchmarks (within 25% variance) ---
        current_avg = sum(market_prices) / market_count if market_count > 0 else None
        for ref_name, ref_data in VERIFIED_BENCHMARKS.items():
                if gpu in ref_data:
                    ref_val = ref_data[gpu]
                    # If no sources, or within 25% of current average
                    is_valid = False
                    if current_avg is None:
                        is_valid = True
                    else:
                        variance = abs(ref_val - current_avg) / current_avg
                        if variance <= 0.25:
                            is_valid = True
                    
                    if is_valid:
                        market_prices.append(ref_val)
                        market_count += 1
                        # Update average for the next benchmark check
                        current_avg = sum(market_prices) / market_count

        # --- PHASE 3: Final Aggregates ---
        market_price = sum(market_prices) / market_count if market_count > 0 else None
        
        # Include Institutional Index in the visual range for dashboard transparency
        all_visual_prices = market_prices + ([inst_price] if inst_price else [])
        min_price = min(all_visual_prices) if all_visual_prices else None
        max_price = max(all_visual_prices) if all_visual_prices else None
        
        # Calculate Weighted Average
        if inst_price and market_price:
            final_avg = (inst_price * 0.5) + (market_price * 0.5)
        elif inst_price:
            final_avg = inst_price
        else:
            final_avg = market_price or 0.0
            
        # Calculate Changes
        old_price_1m = get_historical_avg(c, gpu, month_ago_iso)
        chg_1m = 0.0
        if old_price_1m and old_price_1m > 0:
            chg_1m = ((final_avg - old_price_1m) / old_price_1m) * 100

        old_price_1y = get_historical_avg(c, gpu, year_ago_iso)
        chg_1y = 0.0
        if old_price_1y and old_price_1y > 0:
            chg_1y = ((final_avg - old_price_1y) / old_price_1y) * 100

        stats.append({
            "gpu": gpu,
            "avg_price": final_avg,
            "inst_price": inst_price,
            "market_price": market_price,
            "min_price": min_price,
            "max_price": max_price,
            "chg_1m": chg_1m,
            "chg_1y": chg_1y,
            "source_count": market_count + (1 if inst_price else 0)
        })
    
    log.info(f"Calculated weighted aggregates for {len(stats)} GPU models.")
    
    # 3.5 Inject Weighted Average into History for persistence
    for s in stats:
        history.append({
            "timestamp": last_ts,
            "gpu": s["gpu"],
            "provider": "Neocloud Pulse",
            "price_hourly": s["avg_price"],
            "source": "Weighted (50% Index / 50% Market)",
            "category": "Weighted Average"
        })

    # 4. Save Modular Files
    summary_payload = {
        "latest": latest,
        "stats": stats,
        "last_updated": datetime.now().isoformat()
    }
    history_payload = {
        "history": history
    }
    
    # Write Summary (Small)
    summary_file = DB_PATH.parent / "gpu_intel.js"
    summary_file.write_text(f"window.GPU_INTEL = {json.dumps(summary_payload, indent=2)};", encoding="utf-8")
    
    # Write History (Large)
    history_file = DB_PATH.parent / "gpu_history.js"
    history_file.write_text(f"window.GPU_HISTORY = {json.dumps(history_payload, indent=2)};", encoding="utf-8")
    
    conn.close()
    log.info(f"Intelligence Bridge Finalized (Split into Summary & History).")


if __name__ == "__main__":
    build()

