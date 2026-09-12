import json
from pathlib import Path

STORE_FILE = Path(__file__).resolve().parent.parent / "analysis.json"

# rewrites data to the file, overwriting any previous data
def save_analysis(analysis):
    with STORE_FILE.open("w", encoding="utf-8") as file:
        json.dump(analysis, file, indent=2)

def get_latest_analysis():
    if not STORE_FILE.exists():
        return None

    with STORE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)
