import json
import os
from pathlib import Path


MOCK_DIR = Path(__file__).resolve().parents[2] / "contracts" / "mocks"


def mock(name: str):
    return json.loads((MOCK_DIR / name).read_text(encoding="utf-8"))


def use_mock() -> bool:
    return os.getenv("MOCK", "0") == "1"
