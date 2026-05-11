import sqlite3
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
DB_PATH = ROOT / "database" / "gpu_intel.db"

# Forensic Data Points (Weekly/Monthly) from specialized extraction
SPECIALIZED_DATA = [
    # --- GH200 (Grace Hopper) ---
    ("2024-07-01T00:00:00Z", "GH200", "GetDeploying", 4.50, "gh200_forensics", "Specialized"),
    ("2024-12-01T00:00:00Z", "GH200", "GetDeploying", 3.95, "gh200_forensics", "Specialized"),
    ("2025-06-01T00:00:00Z", "GH200", "GetDeploying", 3.85, "gh200_forensics", "Specialized"),
    ("2026-03-01T00:00:00Z", "GH200", "GetDeploying", 4.20, "gh200_forensics", "Specialized"),
    ("2026-05-01T00:00:00Z", "GH200", "GetDeploying", 4.50, "gh200_forensics", "Specialized"),

    # --- B200 (Blackwell) ---
    ("2025-04-01T00:00:00Z", "B200", "GetDeploying", 5.20, "b200_forensics", "Next-Gen"),
    ("2025-09-01T00:00:00Z", "B200", "GetDeploying", 6.25, "b200_forensics", "Next-Gen"),
    ("2026-02-01T00:00:00Z", "B200", "GetDeploying", 6.90, "b200_forensics", "Next-Gen"),
    ("2026-05-01T00:00:00Z", "B200", "GetDeploying", 7.25, "b200_forensics", "Next-Gen"),

    # --- MI325X (AMD) ---
    ("2025-07-01T00:00:00Z", "MI325X", "GetDeploying", 2.10, "mi325x_forensics", "AMD"),
    ("2025-12-01T00:00:00Z", "MI325X", "GetDeploying", 2.40, "mi325x_forensics", "AMD"),
    ("2026-05-01T00:00:00Z", "MI325X", "GetDeploying", 2.85, "mi325x_forensics", "AMD"),

    # --- H100 Weekly (Jan-May 2026) ---
    ("2026-01-07T00:00:00Z", "H100", "GetDeploying", 3.75, "weekly_wiggle", "Weekly"),
    ("2026-01-21T00:00:00Z", "H100", "GetDeploying", 3.75, "weekly_wiggle", "Weekly"),
    ("2026-02-07T00:00:00Z", "H100", "GetDeploying", 4.12, "weekly_wiggle", "Weekly"),
    ("2026-02-21T00:00:00Z", "H100", "GetDeploying", 4.03, "weekly_wiggle", "Weekly"),
    ("2026-03-07T00:00:00Z", "H100", "GetDeploying", 3.44, "weekly_wiggle", "Weekly"),
    ("2026-03-21T00:00:00Z", "H100", "GetDeploying", 3.30, "weekly_wiggle", "Weekly"),
    ("2026-04-07T00:00:00Z", "H100", "GetDeploying", 3.43, "weekly_wiggle", "Weekly"),
    ("2026-04-21T00:00:00Z", "H100", "GetDeploying", 3.47, "weekly_wiggle", "Weekly"),
    ("2026-05-07T00:00:00Z", "H100", "GetDeploying", 4.76, "weekly_wiggle", "Weekly"),

    # --- H200 Weekly (Jan-May 2026) ---
    ("2026-01-07T00:00:00Z", "H200", "GetDeploying", 4.01, "weekly_wiggle", "Weekly"),
    ("2026-01-21T00:00:00Z", "H200", "GetDeploying", 4.16, "weekly_wiggle", "Weekly"),
    ("2026-02-07T00:00:00Z", "H200", "GetDeploying", 4.15, "weekly_wiggle", "Weekly"),
    ("2026-02-21T00:00:00Z", "H200", "GetDeploying", 3.93, "weekly_wiggle", "Weekly"),
    ("2026-03-07T00:00:00Z", "H200", "GetDeploying", 3.53, "weekly_wiggle", "Weekly"),
    ("2026-03-21T00:00:00Z", "H200", "GetDeploying", 3.60, "weekly_wiggle", "Weekly"),
    ("2026-04-07T00:00:00Z", "H200", "GetDeploying", 3.82, "weekly_wiggle", "Weekly"),
    ("2026-04-21T00:00:00Z", "H200", "GetDeploying", 3.58, "weekly_wiggle", "Weekly")
]

def ingest():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print(f"Ingesting {len(SPECIALIZED_DATA)} high-resolution records...")
    
    for row in SPECIALIZED_DATA:
        # Check if record already exists
        c.execute("SELECT 1 FROM prices WHERE timestamp = ? AND gpu = ? AND provider = ?", (row[0], row[1], row[2]))
        if not c.fetchone():
            c.execute("INSERT INTO prices VALUES (?, ?, ?, ?, ?, ?)", row)
    
    conn.commit()
    conn.close()
    print("Specialized Ingestion Complete.")

if __name__ == "__main__":
    ingest()
