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

load_dotenv()

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "database" / "gpu_intel.db"
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
        conn = sqlite3.connect(DB_PATH)
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
        conn = sqlite3.connect(DB_PATH)
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

            # Look for the sentence "the average sits at $X.XX/hr" or similar in the text
            price = None
            paragraphs = await page.query_selector_all("p")
            for p in paragraphs:
                txt = await p.inner_text()
                # "average sits at $3.15/hr" or "average is $3.15/hr"
                m = re.search(r'average.*?\$(\d+\.?\d*)', txt, re.IGNORECASE)
                if m:
                    price = float(m.group(1))
                    break

            if not price:
                # Fallback 1: just look for the first dollar amount in a strong/bold tag, or large text
                els = await page.query_selector_all("strong, h2, .hero-price")
                for el in els:
                    txt = await el.inner_text()
                    m = re.search(r'\$(\d+\.?\d*)', txt)
                    if m:
                        price = float(m.group(1))
                        break

            if not price:
                # Fallback 2: Calculate median directly from the pricing table
                prices = []
                cells = await page.query_selector_all("td")
                for cell in cells:
                    txt = await cell.inner_text()
                    m = re.search(r'\$(\d+\.\d+)/hr', txt.strip())
                    if m:
                        prices.append(float(m.group(1)))
                if prices:
                    prices.sort()
                    price = prices[len(prices)//2]

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
        await page.wait_for_selector("a.gpu-pricing-row", timeout=15000)
        rows = await page.query_selector_all("a.gpu-pricing-row")
        count = 0
        for row in rows:
            txt = await row.inner_text()
            m = re.search(r'\$\s*(\d+\.\d+)', txt)
            if m:
                name_el = await row.query_selector("div")
                name = (await name_el.inner_text()).strip() if name_el else txt.split('\n')[0].strip()
                gpu = _normalize_gpu(name)
                intel.save(gpu, "RunPod", float(m.group(1)), "runpod.io", "Neocloud")
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

    # Phase 4: Build Intelligence Bridge (Weighted Averages)
    log.info("[4/5] Building Intelligence Bridge with 50/50 weighting...")
    subprocess.run(["python", str(ROOT / "engine" / "build_intel.py")], check=True)

    # Phase 5: Production Sync (SFTP)
    log.info("[5/5] Deploying to Production (bmwseals.com)...")
    subprocess.run(["python", str(ROOT / "engine" / "remote_sync.py")], check=True)


if __name__ == "__main__":
    asyncio.run(main())
