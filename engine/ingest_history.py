import sqlite3
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "database" / "gpu_intel.db"

# Data Points extracted from SemiAnalysis, Silicon Data, and GetDeploying (2024-2026)
# Format: (Date_String, GPU, Provider, Price, Source, Category)
HISTORICAL_DATA = [
    # --- H100 Series (Spot/Market Index) ---
    ("2024-05-01T00:00:00Z", "H100", "SemiAnalysis Spot", 4.80, "semianalysis_forensics", "Market Index"),
    ("2024-07-01T00:00:00Z", "H100", "GetDeploying", 4.20, "getdeploying_forensics", "Neocloud"),
    ("2024-10-01T00:00:00Z", "H100", "SemiAnalysis Spot", 4.30, "semianalysis_forensics", "Market Index"),
    ("2024-12-01T00:00:00Z", "H100", "GetDeploying", 3.60, "getdeploying_forensics", "Neocloud"),
    ("2025-02-01T00:00:00Z", "H100", "SemiAnalysis Spot", 3.10, "semianalysis_forensics", "Market Index"),
    ("2025-06-01T00:00:00Z", "H100", "GetDeploying", 3.30, "getdeploying_forensics", "Neocloud"),
    ("2025-08-01T00:00:00Z", "H100", "SemiAnalysis Spot", 2.90, "semianalysis_forensics", "Market Index"),
    ("2025-10-01T00:00:00Z", "H100", "Silicon Data", 2.75, "silicondata_forensics", "Market Index"),
    ("2025-11-01T00:00:00Z", "H100", "GetDeploying", 4.00, "getdeploying_forensics", "Neocloud"),
    ("2026-01-01T00:00:00Z", "H100", "Vast.ai Median", 1.85, "vast_forensics", "Marketplace"),
    ("2026-03-01T00:00:00Z", "H100", "Silicon Data", 2.35, "silicondata_forensics", "Market Index"),
    ("2026-05-01T00:00:00Z", "H100", "GetDeploying", 3.65, "getdeploying_forensics", "Neocloud"),

    # --- H100 Series (Contract Floor) ---
    ("2024-05-01T00:00:00Z", "H100", "SemiAnalysis 1y", 2.30, "semianalysis_forensics", "Verified Benchmark"),
    ("2024-12-01T00:00:00Z", "H100", "SemiAnalysis 1y", 2.00, "semianalysis_forensics", "Verified Benchmark"),
    ("2025-08-01T00:00:00Z", "H100", "SemiAnalysis 1y", 1.85, "semianalysis_forensics", "Verified Benchmark"),
    ("2025-10-01T00:00:00Z", "H100", "Silicon Data 1y", 1.70, "silicondata_forensics", "Verified Benchmark"),
    ("2026-03-01T00:00:00Z", "H100", "SemiAnalysis 1y", 2.10, "semianalysis_forensics", "Verified Benchmark"),

    # --- H200 Series ---
    ("2025-08-01T00:00:00Z", "H200", "SemiAnalysis Spot", 3.10, "semianalysis_forensics", "Market Index"),
    ("2025-12-01T00:00:00Z", "H200", "SemiAnalysis Spot", 3.40, "semianalysis_forensics", "Market Index"),
    ("2026-03-01T00:00:00Z", "H200", "SemiAnalysis Spot", 3.80, "semianalysis_forensics", "Market Index"),

    # --- B200 (Forecast/Early Pulse) ---
    ("2025-12-01T00:00:00Z", "B200", "Hypothetical Bench", 5.50, "market_forecast", "Forecast"),
    ("2026-05-01T00:00:00Z", "B200", "Early Pulse", 6.20, "market_forecast", "Forecast")
]

def ingest():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Ensure table exists
    c.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            timestamp TEXT,
            gpu TEXT,
            provider TEXT,
            price_hourly REAL,
            source TEXT,
            category TEXT
        )
    """)
    
    print(f"Ingesting {len(HISTORICAL_DATA)} forensic records...")
    
    for row in HISTORICAL_DATA:
        # Check if record already exists (simple dedupe by ts/gpu/provider)
        c.execute("SELECT 1 FROM prices WHERE timestamp = ? AND gpu = ? AND provider = ?", (row[0], row[1], row[2]))
        if not c.fetchone():
            c.execute("INSERT INTO prices VALUES (?, ?, ?, ?, ?, ?)", row)
    
    conn.commit()
    conn.close()
    print("Forensic Ingestion Complete.")

if __name__ == "__main__":
    ingest()
