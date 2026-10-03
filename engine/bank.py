import json
from pathlib import Path

_BANK = None
def _load():
    global _BANK
    if _BANK is None:
        path = Path(__file__).parent / "data" / "mcminer" / "misconception_bank.json"
        _BANK = {item["id"]: item for item in json.loads(path.read_text(encoding="utf-8")) if item.get("meta_data", {}).get("causes_error") == "True"}
    return _BANK

def get_bank_entry(id):
    return _load().get(id)
