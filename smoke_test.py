import json
from pathlib import Path

def test_data():
    # Verify legacy history json
    history_file = Path("database/gpu_history.json")
    assert history_file.exists(), "History file missing"
    with open(history_file, "r") as f:
        history = json.load(f)
    assert len(history) > 0, "No history entries found"
    assert "data" in history[-1], "Latest entry missing data"
    assert len(history[-1]["data"]) > 0, "No price points in latest entry"
    
    # Verify new intelligence bridge
    intel_file = Path("database/gpu_intel.js")
    assert intel_file.exists(), "gpu_intel.js missing"
    content = intel_file.read_text(encoding="utf-8")
    json_str = content.replace("window.GPU_INTEL = ", "").strip().rstrip(";")
    data = json.loads(json_str)
    
    assert "stats" in data, "stats missing in GPU_INTEL"
    for stat in data["stats"]:
        assert "chg_ytd" in stat, f"GPU {stat['gpu']} missing chg_ytd key"
        assert isinstance(stat["chg_ytd"], (int, float)), f"GPU {stat['gpu']} chg_ytd is not numeric"
        
    print(f"PASS: {len(history)} history entries, {len(data['stats'])} GPU stats verified with YTD column.")

if __name__ == "__main__":
    test_data()
