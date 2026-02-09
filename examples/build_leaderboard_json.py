"""Convert leaderboard YAML to JSON for static HTML site."""
import json
import yaml
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "_data"
YAML_PATH = DATA_DIR / "leaderboard.yml"
JSON_PATH = ROOT / "data" / "leaderboard.json"

def main():
    """Convert YAML to JSON."""
    # Read YAML
    with YAML_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    
    # Ensure data directory exists
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Write JSON
    with JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"Converted {YAML_PATH} to {JSON_PATH}")
    print(f"Found {len(data.get('methods', []))} methods")

if __name__ == "__main__":
    main()
