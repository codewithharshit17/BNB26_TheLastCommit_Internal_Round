.PHONY: setup dev-backend dev-frontend mock-backend test eval
setup:
	python -m pip install -r requirements.txt
	cd frontend && npm install
dev-backend:
	python -m uvicorn backend.app.main:app --reload --port 8000
dev-frontend:
	cd frontend && npm run dev
mock-backend:
	set MOCK=1 && python -m uvicorn backend.app.main:app --reload --port 8000
test:
	python -m pytest
eval:
	python -m ml.eval.run --seed 0
