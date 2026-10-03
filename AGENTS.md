# Rules

- Python 3.11+, Node 20. Monorepo, run Python from the repo root (`PYTHONPATH=.`).
- Dependency direction: engine <- ml <- backend. frontend talks to backend over HTTP only.
  engine never imports ml/backend. ml never imports backend.
- Ownership: engine/ = Sukhada, ml/ = Harshit, backend/ = Aneesh, frontend/ = Om,
  contracts/ = shared and frozen after the first hour (add fields, never rename).
- Unimplemented work: raise `NotImplementedError("TODO(<owner>): <what>")`. Never fake results.
- Every Python package folder has `__init__.py` and a `tests/` folder with at least one passing test.
- Windows may be in use: guard `import resource` with try/except ImportError, and
  provide `scripts/*.ps1` equivalents of each Makefile target.

# Step 1: port the starter code (do not change logic)

The folder `_starter/` contains engine.py, posterior.py, api.py, test.py (already tested).

- engine.py -> split into engine/sandbox.py (SAFE builtins, `_worker`, run),
  engine/rewrites/*.py (one transformer per file), engine/rewrites/__init__.py (REGISTRY),
  engine/signature.py (believed_source, signature).
- REGISTRY entries: `{id, transformer, bank_ids, description, held_out}`. Use:
  - noop_method bank_ids [6,7,8,9,10,34,36]
  - range_1_to_n [1]
  - index_1_based [15,66]
  - index_from_m1 [60] held_out=True (never part of the live hypothesis list)
  - assign_copies [13,55]
  - add_before_div [63,64,65]
- posterior.py -> ml/posterior.py unchanged except imports.
- api.py -> backend/app/ (main.py plus routes/ and services/), same behaviour.
- Port test.py into engine/tests and ml/tests. All tests must pass.
- Keep the multiprocessing sandbox working on Windows (spawn): worker function at module level.

# Step 2: contracts/

Create JSON Schema files and mock responses.

Item: `{item_id, kind: diagnostic|probe|transfer|discriminator|retest, family, prompt, code, problem_ref|null}`
POST /answer request: `{session_id, item_id, answer, confidence 1-5}`
POST /answer response: `{posterior:{<hyp>:float}, top, bank_ids:[int], real_output, believed_output,
  believed_source, next:{action: probe|intervene|reassess|done, item?, misconception?}}`
GET /learner/{session_id}: `{misconceptions:[{id, state: active|intervened|suspected_resolved|
  confirmed_resolved|relapsed, posterior_history:[float], evidence:{discriminator_passes,
  surface_forms, delayed_retest}}]}`
GET /intervention/{id}: `{title, bank_description, contrast_code, real_output, believed_output,
  steps:[str], takeaway}`
POST /session/start: `{session_id, item}`

# Step 3: backend/ (FastAPI + SQLite)

- Routes: POST /session/start, POST /answer, GET /learner/{session_id},
  GET /intervention/{id}, GET /health. CORS allow all for dev.
- Pydantic models in app/schemas.py mirror contracts/.
- `MOCK=1` returns matching files from `contracts/mocks/`; `MOCK=0` uses services/diagnosis.py.
- services/resolution.py is a pure state-machine stub with TODO(Aneesh).
- services/learner_store.py + db.py provide SQLite tables sessions, attempts, misconception_state.

# Step 4: frontend/ (Om)

- Next.js TypeScript App Router + Tailwind + recharts.
- Pages: /, /learn, /dashboard, /evidence. Placeholder content only.
- Typed API functions and mock mode live in `src/lib/`.

# Step 5: engine/ and ml/ stubs

- `engine/bank.py` loads the misconception bank and filters string `causes_error == "True"`.
- Stub functions must raise `NotImplementedError("TODO(Sukhada): ...")` or
  `NotImplementedError("TODO(Harshit): ...")` as appropriate.

# Step 6: repo plumbing

- Makefile targets: setup, dev-backend, dev-frontend, mock-backend, test, eval.
- Matching `scripts/*.ps1` scripts are required.
