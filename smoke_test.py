import json
from pathlib import Path

def test_data():
    history_file = Path("database/gpu_history.json")
    assert history_file.exists(), "History file missing"
    
    with open(history_file, "r") as f:
        history = json.load(f)
    
    assert len(history) > 0, "No history entries found"
    assert "data" in history[-1], "Latest entry missing data"
    assert len(history[-1]["data"]) > 0, "No price points in latest entry"
    
    print(f"PASS: {len(history)} history entries, {len(history[-1]['data'])} latest price points.")

if __name__ == "__main__":
    test_data()
