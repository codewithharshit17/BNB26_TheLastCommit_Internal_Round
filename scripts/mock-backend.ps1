$env:MOCK = "1"; python -m uvicorn backend.app.main:app --reload --port 8000
