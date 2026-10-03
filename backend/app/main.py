import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

MOCK_DIR = Path(__file__).resolve().parents[2] / "contracts" / "mocks"


def mock(name: str):
    return json.loads((MOCK_DIR / name).read_text(encoding="utf-8"))


def use_mock() -> bool:
    return os.getenv("MOCK", "0") == "1"


from .routes import router  # noqa: E402

app = FastAPI(title="Re:Learn API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
