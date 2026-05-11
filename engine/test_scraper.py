import asyncio
import logging
from datetime import datetime
from scraper import scrape_getdeploying, scrape_vast, scrape_runpod, scrape_nebius
from stealth_navigator import StealthNavigator

# Configure minimal logging for the test
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger("gpu_test")

class MockGPUIntelligence:
    """A mock intelligence database that just prints to the console instead of writing to SQLite."""
    def __init__(self):
        self.batch_ts = datetime.now().isoformat()
        self.records = []

    def save(self, gpu, provider, price, source, category="Neocloud"):
        record = f"{gpu:<8} | {provider:<15} | ${price:<6.2f} | {category}"
        self.records.append(record)
        log.info(f"  [MOCK DB SAVE] {record}")

async def test_all_scrapers():
    log.info("============================================================")
    log.info("  GPU SCRAPER DIAGNOSTIC TEST (DRY RUN)")
    log.info("============================================================")
    
    mock_intel = MockGPUIntelligence()
    nav = StealthNavigator(headless=True)
    await nav.initialize()

    try:
        log.info("\n--- Testing GetDeploying (Market Index/Aggregator) ---")
        log.info("Note: GetDeploying aggregates 59+ providers into a single median price.")
        await scrape_getdeploying(nav, mock_intel)

        log.info("\n--- Testing Vast.ai (Marketplace) ---")
        await scrape_vast(nav, mock_intel)

        log.info("\n--- Testing RunPod (Marketplace) ---")
        await scrape_runpod(nav, mock_intel)
        
        log.info("\n--- Testing Nebius (Neocloud) ---")
        await scrape_nebius(nav, mock_intel)
        
    finally:
        await nav.close()
        
    log.info("\n============================================================")
    log.info(f"  TEST COMPLETE: Successfully scraped {len(mock_intel.records)} live data points.")
    log.info("  No data was written to the production SQLite database.")
    log.info("============================================================")

if __name__ == "__main__":
    asyncio.run(test_all_scrapers())
