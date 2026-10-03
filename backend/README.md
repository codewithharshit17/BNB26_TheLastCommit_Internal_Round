# backend

Owner: Aneesh. FastAPI routes expose session, answer, learner, intervention, and health contracts, with SQLite persistence and a mock mode. It consumes `ml` and `engine`; run `uvicorn backend.app.main:app --reload` or `pytest backend/tests`.
