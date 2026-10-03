# Re:Learn

Re:Learn is a misconception-diagnosis tutor for introductory Python. It uses
the engine signatures, Bayesian diagnosis, information-gain probes, learner
state tracking, and a small Next.js demo frontend.

## Requirements

- Python 3.11 or newer
- Node.js 20 or newer
- npm
- A writable checkout (the frontend build writes `.next/` and Next.js type files)

Run Python commands from the repository root so `PYTHONPATH=.` resolves the
`engine`, `ml`, and `backend` packages correctly.

## First-time setup

From the repository root:

```bash
python -m pip install -r requirements.txt
cd frontend
npm install
cd ..
```

PowerShell equivalents are available under `scripts/`:

```powershell
.\scripts\setup.ps1
```

If PowerShell blocks local scripts, run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\setup.ps1
```

## Run the real end-to-end demo

Use two terminals, both started from the repository root.

Terminal 1 — backend with real diagnosis:

```bash
MOCK=0 python -m uvicorn backend.app.main:app --reload --port 8000
```

PowerShell:

```powershell
$env:MOCK = "0"
python -m uvicorn backend.app.main:app --reload --port 8000
```

Terminal 2 — frontend connected to the backend:

```bash
cd frontend
NEXT_PUBLIC_API_BASE=http://localhost:8000 NEXT_PUBLIC_MOCK=0 npm run dev
```

PowerShell:

```powershell
cd frontend
$env:NEXT_PUBLIC_API_BASE = "http://localhost:8000"
$env:NEXT_PUBLIC_MOCK = "0"
npm run dev
```

Open [http://localhost:3000](http://localhost:3000), then use `/learn`.
Check the backend first with:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{"ok": true}
```

The live `/answer` response includes the posterior, top hypothesis, bank IDs,
real output, believed output/source, flat next-action fields, and the nested
`next` object.

## Mock/demo mode

Mock mode lets the frontend work without a live diagnosis session. Run the
backend in one terminal:

```bash
MOCK=1 python -m uvicorn backend.app.main:app --reload --port 8000
```

Then run the frontend with `NEXT_PUBLIC_MOCK=1`. The frontend reads the mock
contract responses from `contracts/mocks/`; it does not exercise the real ML
pipeline.

PowerShell:

```powershell
.\scripts\mock-backend.ps1
```

Use live mode for the final end-to-end diagnosis demo.

## Testing

Recommended focused validation from the repository root:

```bash
python -m pytest engine ml -q
python -m pytest backend/tests backend/app/services/tests -q
```

Current expected results are 158 engine/ML tests and 10 focused backend tests.

Frontend type-check:

```bash
cd frontend
npx tsc --noEmit --incremental false
cd ..
```

The repository also contains Make targets:

```bash
make setup
make test
make dev-backend
make dev-frontend
```

`make eval` is an older convenience target that uses seed `0`; use the
explicit seed-42 commands below for the reproducible demo report.

On Windows, prefer the matching scripts:

```powershell
.\scripts\test.ps1
.\scripts\dev-backend.ps1
.\scripts\dev-frontend.ps1
```

The full repository suite includes known unrelated collection/import checks.
Use the focused commands above when validating the demo path.

## Evaluation and charts

Run the deterministic evaluation and chart generation from the repository root:

```bash
python -m ml.eval.run --seed 42
python -m ml.eval.charts
```

Outputs are written to:

- `eval/out/metrics.json`
- `eval/out/charts/classifier_accuracy.png`
- `eval/out/charts/probe_overall.png`
- `eval/out/charts/probe_confusable.png`
- `eval/out/charts/false_resolution.png`
- `eval/out/charts/heldout_safety.png`
- `eval/out/charts/ablations.png`

The LLM baseline is optional. Without `LLM_API_KEY`, evaluation continues and
records the baseline as skipped.

The resolution state machine requires multiple discriminator/surface-form
passes and a delayed retest; one correct answer cannot confirm resolution.

## API smoke checks

Start a session:

```bash
curl -X POST http://localhost:8000/session/start
```

Submit the initial answer using the returned `session_id`:

```bash
curl -X POST http://localhost:8000/answer \
  -H "Content-Type: application/json" \
  -d '{"session_id":"SESSION_ID","item_id":"i1","answer":"10","confidence":5}'
```

For an intervention, use the returned misconception ID:

```bash
curl "http://localhost:8000/intervention/index_1_based?item_id=i1&session_id=SESSION_ID"
```

## Data and safety notes

- `index_from_m1` is held out and excluded from live diagnosis.
- Bank IDs are filtered against the loaded misconception bank. The invalid
  `noop_method` mapping entry `34` is not fabricated into live responses.
- SQLite data is stored in `relearn.db` by default. Set `RELEARN_DB_PATH` to
  use another database path for a clean demo session.
- No LLM key is required for the core pipeline.
- Authentication, production deployment, and persistent frontend session
  management are outside this hackathon skeleton.


Do not commit generated databases or environment secrets. Keep `LLM_API_KEY`
empty unless the optional baseline is intentionally being demonstrated.
