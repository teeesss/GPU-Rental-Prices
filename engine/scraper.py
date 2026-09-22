import asyncio
import logging
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from stealth_navigator import StealthNavigator
from index_scraper import scrape_indices
import subprocess
import sys

load_dotenv()

ROOT = Path(__file__).parent.parent
DB_PATH = Path(os.environ.get("GPU_DB_PATH", ROOT / "database" / "gpu_intel.db"))
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler(LOG_DIR / "scraper.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger("gpu_scraper")

# ── Hardcoded fallback benchmarks (updated quarterly) ──────────────────────────
VERIFIED_BENCHMARKS = {
    "Institutional Ref": {"H100": 2.55, "H200": 3.10, "B200": 5.10, "GB200": 4.50, "GH200": 3.20, "A100": 1.25, "B300": 5.50, "MI325X": 2.25, "MI355X": 4.50},
    "Neo-Cloud Ref":    {"H100": 3.15, "H200": 3.95, "B200": 5.50, "GB200": 5.00, "GH200": 3.10, "A100": 1.45, "B300": 5.90, "MI325X": 2.50, "MI355X": 5.45},
    "Marketplace Ref":  {"H100": 1.85, "H200": 2.95, "B200": 3.90, "GB200": 4.25, "GH200": 2.85, "A100": 0.75, "B300": 4.50, "MI325X": 1.95, "MI355X": 3.95},
}

# ── GetDeploying GPU slugs to scrape ────────────────────────────────────────────
GETDEPLOYING_TARGETS = [
    ("https://getdeploying.com/gpus/nvidia-h100",  "H100"),
    ("https://getdeploying.com/gpus/nvidia-h200",  "H200"),
    ("https://getdeploying.com/gpus/nvidia-b200",  "B200"),
    ("https://getdeploying.com/gpus/nvidia-b300",  "B300"),
    ("https://getdeploying.com/gpus/nvidia-gb200", "GB200"),
    ("https://getdeploying.com/gpus/nvidia-gh200", "GH200"),
    ("https://getdeploying.com/gpus/amd-mi325x",   "MI325X"),
    ("https://getdeploying.com/gpus/amd-mi355x",   "MI355X"),
]



class GPUIntelligence:
    def __init__(self):
        self.batch_ts = datetime.now(timezone.utc).isoformat()
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(DB_PATH, timeout=30)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                timestamp    TEXT,
                gpu          TEXT,
                provider     TEXT,
                price_hourly REAL,
                source       TEXT,
                category     TEXT
            )
        """)
        conn.commit()
        conn.close()

    def save(self, gpu, provider, price, source, category="Neocloud"):
        conn = sqlite3.connect(DB_PATH, timeout=30)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute(
            "INSERT INTO prices VALUES (?,?,?,?,?,?)",
            (self.batch_ts, gpu, provider, price, source, category)
        )
        conn.commit()
        conn.close()


# ── Live scrapers ───────────────────────────────────────────────────────────────

async def scrape_getdeploying(nav, intel):
    """Scrape GetDeploying's per-GPU page for the current market median price."""
    for url, gpu_model in GETDEPLOYING_TARGETS:
        page = await nav.context.new_page()
        try:
            await nav.ghost_browse(page, url)
            await page.wait_for_load_state("networkidle", timeout=20000)

            price = None

            # Strategy 1: "Median price (current)" stat card badge
            dts = await page.query_selector_all("dt")
            for dt in dts:
                txt = await dt.inner_text()
                if "median price" in txt.lower():
                    dd = await dt.evaluate_handle("el => el.nextElementSibling")
                    if dd:
                        dd_txt = await dd.inner_text()
                        m = re.search(r'\$(\d+\.?\d*)', dd_txt)
                        if m:
                            price = float(m.group(1))
                            break

            # Strategy 2: Schema.org JSON-LD FAQ/Metadata
            if not price:
                scripts = await page.query_selector_all("script[type='application/ld+json']")
                for s in scripts:
                    content = await s.inner_text()
                    m = re.search(r'median on-demand price is \$(\d+\.?\d*)', content, re.IGNORECASE)
                    if m:
                        price = float(m.group(1))
                        break

            # Strategy 3: Narrative paragraphs/headings mentioning median or average
            if not price:
                paragraphs = await page.query_selector_all("p, h2, strong, .hero-price")
                for p in paragraphs:
                    txt = await p.inner_text()
                    m = re.search(r'(?:median|average).*?\$(\d+\.?\d*)', txt, re.IGNORECASE)
                    if m:
                        val = float(m.group(1))
                        if 0.1 <= val <= 100.0:
                            price = val
                            break

            # Strategy 4: Calculate median directly from pricing table td cells
            if not price:
                prices = []
                cells = await page.query_selector_all("td")
                for cell in cells:
                    txt = (await cell.inner_text()).strip()
                    m = re.search(r'^\$(\d+\.?\d*)(?:/hr)?$', txt)
                    if m:
                        val = float(m.group(1))
                        if 0.1 <= val <= 100.0:
                            prices.append(val)
                if prices:
                    prices.sort()
                    price = prices[len(prices) // 2]

            if price:
                log.info(f"  GetDeploying {gpu_model}: ${price:.2f}/hr")
                intel.save(gpu_model, "GetDeploying", price, "getdeploying.com", "Market Index")
            else:
                log.warning(f"  GetDeploying {gpu_model}: price not found")
        except Exception as e:
            log.error(f"  GetDeploying {gpu_model} error: {e}")
        finally:
            await page.close()
        await asyncio.sleep(3)  # polite delay between pages


async def scrape_vast(nav, intel):
    page = await nav.context.new_page()
    try:
        await nav.ghost_browse(page, "https://vast.ai/pricing")
        await page.wait_for_selector("a[href^='/pricing/gpu/']", timeout=15000)
        cards = await page.query_selector_all("a[href^='/pricing/gpu/']")
        count = 0
        for card in cards:
            txt = await card.inner_text()
            name_el = await card.query_selector("h3, strong, div[class*='name'], div[class*='title']")
            if name_el:
                name = (await name_el.inner_text()).strip()
            else:
                # Fallback: first line is usually the name
                name = txt.split('\n')[0].strip()
            
            m = re.search(r'\$\s*(\d+\.\d+)', txt)
            if m and name:
                price = float(m.group(1))
                gpu = _normalize_gpu(name)
                intel.save(gpu, "Vast.ai", price, "vast.ai", "Marketplace")
                count += 1
        log.info(f"  Vast.ai: {count} listings saved")
    except Exception as e:
        log.error(f"  Vast.ai error: {e}")
    finally:
        await page.close()


async def scrape_runpod(nav, intel):
    page = await nav.context.new_page()
    try:
        await nav.ghost_browse(page, "https://www.runpod.io/gpu-instance/pricing")
        await page.wait_for_selector(".gpu_table-row", timeout=15000)
        rows = await page.query_selector_all(".gpu_table-row")
        count = 0
        for row in rows:
            name_el = await row.query_selector(".gpu_name")
            price_el = await row.query_selector(".gpu_table-price, .active-price")
            if name_el and price_el:
                name = (await name_el.inner_text()).strip()
                price_txt = (await price_el.inner_text()).strip()
                m = re.search(r'(\d+\.\d+)', price_txt)
                if m:
                    price = float(m.group(1))
                    gpu = _normalize_gpu(name)
                    intel.save(gpu, "RunPod", price, "runpod.io", "Neocloud")
                    count += 1
        log.info(f"  RunPod: {count} listings saved")
    except Exception as e:
        log.error(f"  RunPod error: {e}")
    finally:
        await page.close()



async def scrape_nebius(nav, intel):
    page = await nav.context.new_page()
    try:
        await nav.ghost_browse(page, "https://nebius.com/prices")
        # Wait for either table or main content
        await page.wait_for_selector("table, .pricing-table, h2", timeout=15000)
        
        # Nebius DOM is often nested divs or grids. The most resilient approach is line-by-line body parsing.
        body_text = await page.inner_text("body")
        lines = [line.strip() for line in body_text.split('\n') if line.strip()]
        
        count = 0
        current_gpu = None
        prices = []
        
        for line in lines:
            if line.startswith("NVIDIA "):
                # Save previous GPU
                if current_gpu and prices:
                    price = min(prices)
                    gpu = _normalize_gpu(current_gpu)
                    intel.save(gpu, "Nebius", price, "nebius.com", "Neocloud")
                    count += 1
                current_gpu = line
                prices = []
            elif current_gpu and "$" in line:
                m = re.search(r'\$(\d+\.\d+)', line)
                if m:
                    prices.append(float(m.group(1)))
            # Stop if we hit the CPU or Storage sections
            elif current_gpu and ("CPU-only" in line or line == "Storage"):
                if prices:
                    price = min(prices)
                    gpu = _normalize_gpu(current_gpu)
                    intel.save(gpu, "Nebius", price, "nebius.com", "Neocloud")
                    count += 1
                current_gpu = None

        # Catch the last one if we reached the end of the lines
        if current_gpu and prices:
            price = min(prices)
            gpu = _normalize_gpu(current_gpu)
            intel.save(gpu, "Nebius", price, "nebius.com", "Neocloud")
            count += 1
            
        log.info(f"  Nebius: {count} listings saved")
    except Exception as e:
        log.error(f"  Nebius error: {e}")
    finally:
        await page.close()


def _normalize_gpu(name: str) -> str:
    """Map raw GPU strings to canonical model names."""
    name = name.upper()
    for model in ["H100", "H200", "B200", "B300", "GH200", "GB200", "A100", "A10", "MI325X", "MI300X", "L40S", "L40", "RTX PRO 6000"]:
        if model in name:
            return model
    return name.replace("NVIDIA", "").replace("AMD", "").strip()


# ── Entry point ─────────────────────────────────────────────────────────────────

async def main():
    log.info("=" * 60)
    log.info("  GPU NEOCLOUD INTELLIGENCE — DAILY PULSE")
    log.info(f"  Batch: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    log.info("=" * 60)

    temp_db_env = os.environ.get("GPU_DB_PATH")
    main_db_path = ROOT / "database" / "gpu_intel.db"

    # If using a temp DB, clear it first so we only gather new data for this batch
    if temp_db_env and Path(temp_db_env) != main_db_path:
        temp_db_path = Path(temp_db_env)
        if temp_db_path.exists():
            try:
                temp_db_path.unlink()
                log.info(f"Cleared old temp database: {temp_db_path}")
            except Exception as e:
                log.warning(f"Could not clear old temp database: {e}")

    intel = GPUIntelligence()
    nav   = StealthNavigator(headless=True)
    await nav.initialize()

    # Phase 1: Live market scrape — GetDeploying
    log.info("[1/4] Scraping GetDeploying live market prices...")
    await scrape_getdeploying(nav, intel)

    # Phase 2: Institutional Index scrape — ComputePulse
    log.info("[2/4] Extracting institutional indices (ComputePulse)...")
    try:
        await scrape_indices(nav, intel) 
    except Exception as e:
        log.error(f"Institutional Index scrape failed: {e}")

    # Phase 3: Marketplace scrapers
    log.info("[3/4] Extracting marketplace data (Vast/RunPod/Nebius)...")
    await scrape_vast(nav, intel)
    await scrape_runpod(nav, intel)
    await scrape_nebius(nav, intel)

    log.info(f"Pulse complete. Batch: {intel.batch_ts}")
    await nav.close()

    # Merge Temp DB into Main DB
    if temp_db_env and Path(temp_db_env) != main_db_path:
        temp_db_path = Path(temp_db_env)
        if temp_db_path.exists():
            if main_db_path.exists():
                log.info("Merging temp database records into main database...")
                
                # Backup main database
                backup_path = main_db_path.with_suffix(".db.bak")
                try:
                    import shutil
                    shutil.copy2(main_db_path, backup_path)
                    log.info(f"Backed up main database to {backup_path}")
                except Exception as e:
                    log.error(f"Failed to back up database: {e}")
                
                # Merge records
                try:
                    main_conn = sqlite3.connect(main_db_path, timeout=30)
                    main_conn.execute("PRAGMA journal_mode=WAL")
                    main_conn.execute(f"ATTACH DATABASE '{temp_db_path.as_posix()}' AS temp_db")
                    main_conn.execute("INSERT OR IGNORE INTO prices SELECT * FROM temp_db.prices")
                    main_conn.commit()
                    main_conn.close()
                    log.info("Successfully merged new records into main database.")
                    
                    # Delete temp database after successful merge
                    temp_db_path.unlink()
                except Exception as e:
                    log.error(f"Failed to merge databases: {e}")
                    raise e
            else:
                # If main DB doesn't exist, initialize it from temp
                main_db_path.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(temp_db_path, main_db_path)
                log.info("Initialized main database with new scraped data.")
                temp_db_path.unlink()

        # Update environment variable so child subprocesses use the main database
        os.environ["GPU_DB_PATH"] = str(main_db_path)

    # Phase 4: Build Intelligence Bridge (Weighted Averages)
    log.info("[4/5] Building Intelligence Bridge with 50/50 weighting...")
    subprocess.run([sys.executable, str(ROOT / "engine" / "build_intel.py")], check=True)

    # Phase 5: Production Sync (SFTP)
    log.info("[5/5] Deploying to Production (bmwseals.com)...")
    subprocess.run([sys.executable, str(ROOT / "engine" / "remote_sync.py")], check=True)



if __name__ == "__main__":
    asyncio.run(main())
