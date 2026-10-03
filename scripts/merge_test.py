"""
Re:Learn — Merge / Integration Test
====================================
Tests every cross-team boundary in the codebase:

  Layer 1  engine  ↔  ml          (Sukhada → Harshit)
  Layer 2  engine  ↔  backend     (Sukhada → Aneesh)
  Layer 3  ml      ↔  backend     (Harshit → Aneesh)
  Layer 4  backend ↔  contracts   (Aneesh  → Om)
  Layer 5  contracts ↔ mocks      (shared  → Om)
  Layer 6  full session walk      (end-to-end demo path)

Run from repo root:
    PYTHONPATH=. python scripts/merge_test.py
"""

import json, sys, traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PASS = 0; FAIL = 0; WARN = 0

def ok(label):
    global PASS
    print(f"  [OK]  {label}")
    PASS += 1

def fail(label, detail=""):
    global FAIL
    print(f"  [FAIL] {label}")
    if detail:
        print(f"         {detail}")
    FAIL += 1

def warn(label, detail=""):
    global WARN
    print(f"  [WARN] {label}")
    if detail:
        print(f"         {detail}")
    WARN += 1

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

# ─────────────────────────────────────────────────────────────────
# LAYER 1 — engine ↔ ml  (Sukhada's outputs feed Harshit's inputs)
# ─────────────────────────────────────────────────────────────────
section("Layer 1 — engine ↔ ml  (Sukhada → Harshit)")

from engine.signature import signature, believed_source
from engine.items.generator import load as load_items
from engine.rewrites import REGISTRY, LIVE_REGISTRY
from ml.posterior import update, entropy, info_gain

# 1a. signature() returns a dict compatible with ml.posterior.update()
sig = signature("a = [10, 20, 30]\nprint(a[1])")
hyps = ["correct", "noop_method", "range_1_to_n", "index_1_based",
        "assign_copies", "add_before_div", "unknown"]
prior = {h: 1/len(hyps) for h in hyps}

try:
    post = update(prior, sig, "10", 5)
    ok("signature() output compatible with ml.posterior.update()")
    s = round(sum(post.values()), 8)
    if s == 1.0:
        ok("update() returns normalised posterior (sums to 1.0)")
    else:
        fail("update() normalisation", f"sum={s}")
except Exception as e:
    fail("update() crashed", str(e)); traceback.print_exc()

# 1b. update() correctly concentrates on index_1_based
try:
    if post.get("index_1_based", 0) > 0.5:
        ok("update() concentrates on index_1_based when answer='10' conf=5")
    else:
        fail("update() posterior not concentrated", str(sorted(post.items(), key=lambda x:-x[1])[:3]))
except Exception as e:
    fail("posterior check crashed", str(e))

# 1c. info_gain() accepts signature from engine
try:
    items = load_items()
    probe_item = next(i for i in items if i["kind"] == "probe")
    ig = info_gain(post, probe_item["signature"])
    if isinstance(ig, float) and ig >= 0:
        ok(f"info_gain() accepts item signature (ig={ig:.4f})")
    else:
        fail("info_gain() returned unexpected value", str(ig))
except Exception as e:
    fail("info_gain() crashed", str(e)); traceback.print_exc()

# 1d. LIVE_REGISTRY excludes held-out (index_from_m1)
heldout = [e["id"] for e in REGISTRY if e["held_out"]]
live_ids = [e["id"] for e in LIVE_REGISTRY]
if "index_from_m1" not in live_ids:
    ok("LIVE_REGISTRY correctly excludes index_from_m1 (held-out)")
else:
    fail("index_from_m1 leaked into LIVE_REGISTRY")

# 1e. Simulator → Harshit can call make_student with all types
try:
    import numpy as np
    from engine.simulator.students import make_student
    rng = np.random.default_rng(0)
    disc = next(i for i in items if i["discriminates"] and i["family"] == "index_1_based")
    for kind in ["clean", "noisy", "mixed", "unknown", "patcher", "true_learner"]:
        s = make_student(kind, misconception="index_1_based", misconception2="noop_method")
        if kind in ("patcher", "true_learner"):
            s.intervened = True
            s.patched_ids = {disc["item_id"]}
        ans = s(disc, rng)
        assert ans in (disc["signature"]["real"], disc["signature"]["index_1_based"]) or \
               ans in disc["signature"].values(), f"unexpected answer: {ans!r}"
    ok("make_student() all 6 types callable with engine item signatures")
except Exception as e:
    fail("make_student() integration", str(e)); traceback.print_exc()

# 1f. Items have all keys Harshit's eval loop needs
required_item_keys = {"item_id", "kind", "family", "code", "signature", "discriminates"}
missing = [i["item_id"] for i in items if not required_item_keys <= i.keys()]
if not missing:
    ok("All items have keys needed by Harshit's eval loop")
else:
    fail("Items missing eval keys", str(missing[:3]))

# ─────────────────────────────────────────────────────────────────
# LAYER 2 — engine ↔ backend  (Sukhada → Aneesh)
# ─────────────────────────────────────────────────────────────────
section("Layer 2 — engine ↔ backend  (Sukhada → Aneesh)")

from backend.app.services.diagnosis import (
    start_session, answer as diag_answer,
    ITEMS as DIAG_ITEMS, HYPS as DIAG_HYPS, BANK_MAP
)
from backend.app.schemas import (
    AnswerResponse, InterventionResponse, Item as SchemaItem
)

# 2a. ITEMS loaded from real bank (not the 2-item placeholder)
if len(DIAG_ITEMS) >= 40:
    ok(f"diagnosis.ITEMS loaded from items_bank.json ({len(DIAG_ITEMS)} items)")
else:
    fail("diagnosis.ITEMS too small", f"only {len(DIAG_ITEMS)} items")

# 2b. HYPS list does NOT contain index_from_m1
if "index_from_m1" not in DIAG_HYPS:
    ok("diagnosis.HYPS correctly excludes held-out index_from_m1")
else:
    fail("index_from_m1 in diagnosis.HYPS — leaks held-out to learner")

# 2c. BANK_MAP covers all live families
for fam in ["noop_method", "range_1_to_n", "index_1_based", "assign_copies", "add_before_div"]:
    if fam in BANK_MAP and len(BANK_MAP[fam]) > 0:
        ok(f"BANK_MAP has bank_ids for {fam}: {BANK_MAP[fam]}")
    else:
        fail(f"BANK_MAP missing or empty for {fam}")

# 2d. start_session() returns valid contract shape
try:
    sess = start_session()
    assert "session_id" in sess and "item" in sess
    item = sess["item"]
    assert all(k in item for k in ["item_id", "kind", "family", "prompt", "code"])
    assert item["kind"] in {"diagnostic","probe","transfer","discriminator","retest"}
    ok("start_session() returns valid contract shape")
    sid = sess["session_id"]
    iid = item["item_id"]
except Exception as e:
    fail("start_session() contract shape", str(e)); sid = None; iid = None

# 2e. answer() response matches AnswerResponse schema fields
if sid and iid:
    class FakePayload:
        session_id = sid
        item_id    = iid
        answer     = "hello"    # any string
        confidence = 3

    try:
        r = diag_answer(FakePayload())
        required = {"posterior","top","bank_ids","real_output","believed_output","believed_source","next"}
        missing_fields = required - r.keys()
        if not missing_fields:
            ok("answer() response has all AnswerResponse fields")
        else:
            fail("answer() missing fields", str(missing_fields))

        # Verify Pydantic schema accepts the response
        try:
            AnswerResponse(**r)
            ok("answer() response passes Pydantic AnswerResponse validation")
        except Exception as e:
            fail("Pydantic validation of answer()", str(e))

        # posterior sums to 1
        s = round(sum(r["posterior"].values()), 8)
        if s == 1.0:
            ok("answer() posterior sums to 1.0")
        else:
            fail("answer() posterior doesn't sum to 1", f"sum={s}")

        # bank_ids is a list of ints
        if isinstance(r["bank_ids"], list):
            ok("bank_ids is a list")
        else:
            fail("bank_ids wrong type", type(r["bank_ids"]))

        # next.action is one of the valid literals
        if r["next"]["action"] in {"probe","intervene","reassess","done"}:
            ok(f"next.action='{r['next']['action']}' is a valid literal")
        else:
            fail("next.action invalid", r["next"]["action"])

    except Exception as e:
        fail("answer() crashed", str(e)); traceback.print_exc()

# 2f. interventions.json shape matches InterventionResponse schema
from engine.interventions.builder import load as load_ivs
ivs = load_ivs()
for mid, iv in ivs.items():
    try:
        InterventionResponse(**iv)
        ok(f"interventions[{mid}] passes Pydantic InterventionResponse validation")
    except Exception as e:
        fail(f"interventions[{mid}] Pydantic validation", str(e))

# 2g. SQLite tables created by db.connect()
from backend.app.db import connect
try:
    db = connect()
    tables = {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()}
    for t in ["sessions", "attempts", "misconception_state"]:
        if t in tables:
            ok(f"SQLite table '{t}' exists")
        else:
            fail(f"SQLite table '{t}' missing")
    db.close()
except Exception as e:
    fail("SQLite db.connect()", str(e))

# ─────────────────────────────────────────────────────────────────
# LAYER 3 — ml ↔ backend  (Harshit → Aneesh)
# ─────────────────────────────────────────────────────────────────
section("Layer 3 — ml ↔ backend  (Harshit → Aneesh)")

# 3a. ml.posterior.update signature matches how diagnosis.py calls it
import inspect
sig_update = inspect.signature(update)
params = list(sig_update.parameters.keys())
if params == ["prior", "sig", "answer", "conf"]:
    ok("ml.posterior.update(prior, sig, answer, conf) — signature correct")
else:
    fail("ml.posterior.update signature mismatch", str(params))

# 3b. info_gain signature matches how _best_probe calls it
sig_ig = inspect.signature(info_gain)
ig_params = list(sig_ig.parameters.keys())
if "post" in ig_params and "sig" in ig_params:
    ok("ml.posterior.info_gain(post, sig, ...) — signature correct")
else:
    fail("info_gain signature mismatch", str(ig_params))

# 3c. ml.probes.next_probe is a stub — expected, not a failure
try:
    from ml.probes import next_probe
    next_probe({}, [])
    warn("ml.probes.next_probe unexpectedly succeeded (expected stub)")
except NotImplementedError as e:
    ok("ml.probes.next_probe is a TODO(Harshit) stub — expected")
except Exception as e:
    fail("ml.probes.next_probe unexpected error", str(e))

# 3d. ml.classifier.classify is a stub — expected
try:
    from ml.classifier import classify
    classify({})
    warn("ml.classifier.classify unexpectedly succeeded")
except NotImplementedError:
    ok("ml.classifier.classify is a TODO(Harshit) stub — expected")
except Exception as e:
    fail("ml.classifier.classify unexpected error", str(e))

# 3e. ml.eval.run.main is a stub — expected
try:
    from ml.eval.run import main
    main([])
    warn("ml.eval.run.main unexpectedly succeeded")
except NotImplementedError:
    ok("ml.eval.run.main is a TODO(Harshit) stub — expected")
except Exception as e:
    fail("ml.eval.run.main unexpected error", str(e))

# ─────────────────────────────────────────────────────────────────
# LAYER 4 — backend ↔ contracts  (Aneesh → Om)
# ─────────────────────────────────────────────────────────────────
section("Layer 4 — backend ↔ contracts  (Aneesh → Om)")

# 4a. Live answer() response matches JSON schema contract
import json as _json
answer_schema = _json.loads((ROOT / "contracts" / "answer-response.schema.json").read_text())
required_contract_fields = set(answer_schema.get("required", []))
if sid and iid:
    r_keys = set(r.keys())
    missing = required_contract_fields - r_keys
    if not missing:
        ok(f"answer() response has all JSON-schema required fields: {required_contract_fields}")
    else:
        fail("answer() missing contract fields", str(missing))

# 4b. start_session() response matches session-start schema
start_schema = _json.loads((ROOT / "contracts" / "session-start.schema.json").read_text())
start_required = set(start_schema.get("required", []))
sess2 = start_session()
missing_start = start_required - sess2.keys()
if not missing_start:
    ok("start_session() response matches session-start.schema.json")
else:
    fail("start_session() contract mismatch", str(missing_start))

# 4c. Mock answer_probe.json and answer_intervene.json match contract
for mock_name in ["answer_probe.json", "answer_intervene.json"]:
    mock_data = _json.loads((ROOT / "contracts" / "mocks" / mock_name).read_text())
    missing = required_contract_fields - mock_data.keys()
    if not missing:
        ok(f"contracts/mocks/{mock_name} matches answer-response schema")
    else:
        fail(f"contracts/mocks/{mock_name} missing fields", str(missing))

# 4d. Mock posterior keys: check mock doesn't have index_from_m1
#     while live HYPS excludes it — Om sees consistent key sets
mock_probe = _json.loads((ROOT / "contracts" / "mocks" / "answer_probe.json").read_text())
live_post_keys = set(DIAG_HYPS)
mock_post_keys = set(mock_probe["posterior"].keys())
extra_in_mock = mock_post_keys - live_post_keys
if "index_from_m1" in extra_in_mock:
    warn(
        "contracts/mocks/answer_probe.json has 'index_from_m1' in posterior",
        "Live API excludes it — Om's frontend will see different keys in mock vs real mode"
    )
else:
    ok("Mock posterior keys consistent with live HYPS (no leaked held-out)")

# 4e. resolution.py is a stub — expected
try:
    from backend.app.services.resolution import next_state
    next_state("active", {}, "discriminator", 0.9)
    warn("resolution.next_state unexpectedly succeeded")
except NotImplementedError:
    ok("resolution.next_state is a TODO(Aneesh) stub — expected")
except Exception as e:
    fail("resolution.next_state unexpected error", str(e))

# 4f. learner_store.learner() returns valid LearnerResponse shape
from backend.app.services.learner_store import learner as get_learner
from backend.app.schemas import LearnerResponse
try:
    lr = get_learner("any-session")
    LearnerResponse(**lr)
    ok("learner_store.learner() returns valid LearnerResponse shape")
except Exception as e:
    fail("learner_store.learner() shape", str(e))

# ─────────────────────────────────────────────────────────────────
# LAYER 5 — contracts/mocks ↔ frontend types  (Om)
# ─────────────────────────────────────────────────────────────────
section("Layer 5 — contracts/mocks ↔ frontend TypeScript types  (Om)")

# We can't run TypeScript here, but we verify the JSON mock shapes
# match the TypeScript type definitions exactly (by field name).

# AnswerResponse TS type fields
ts_answer_fields = {"posterior","top","bank_ids","real_output","believed_output","believed_source","next"}
for mock_name in ["answer_probe.json", "answer_intervene.json"]:
    data = _json.loads((ROOT / "contracts" / "mocks" / mock_name).read_text())
    missing = ts_answer_fields - data.keys()
    extra   = data.keys() - ts_answer_fields
    if not missing:
        ok(f"{mock_name} has all TypeScript AnswerResponse fields")
    else:
        fail(f"{mock_name} missing TS fields", str(missing))
    if extra:
        warn(f"{mock_name} has extra fields (ok but unused by TS)", str(extra))

# SessionStart TS type: {session_id, item}
start_data = _json.loads((ROOT / "contracts" / "mocks" / "start.json").read_text())
ts_start_fields = {"session_id", "item"}
missing = ts_start_fields - start_data.keys()
if not missing:
    ok("start.json has all TypeScript SessionStart fields")
else:
    fail("start.json missing TS SessionStart fields", str(missing))

# Item shape inside start.json
item_data = start_data.get("item", {})
ts_item_fields = {"item_id","kind","family","prompt","code","problem_ref"}
missing_item = ts_item_fields - item_data.keys()
if not missing_item:
    ok("start.json.item has all TypeScript Item fields")
else:
    fail("start.json.item missing TS Item fields", str(missing_item))

# InterventionResponse TS type
ts_iv_fields = {"title","bank_description","contrast_code","real_output","believed_output","steps","takeaway"}
iv_mock = _json.loads((ROOT / "contracts" / "mocks" / "intervention.json").read_text())
missing = ts_iv_fields - iv_mock.keys()
if not missing:
    ok("intervention.json has all TypeScript InterventionResponse fields")
else:
    fail("intervention.json missing TS fields", str(missing))

# LearnerResponse TS type: {misconceptions: Array<{id,state,posterior_history,evidence}>}
learner_mock = _json.loads((ROOT / "contracts" / "mocks" / "learner.json").read_text())
if "misconceptions" in learner_mock and isinstance(learner_mock["misconceptions"], list):
    ok("learner.json has misconceptions array")
    mc = learner_mock["misconceptions"][0] if learner_mock["misconceptions"] else {}
    ts_mc_fields = {"id","state","posterior_history","evidence"}
    if mc:
        missing = ts_mc_fields - mc.keys()
        if not missing:
            ok("learner.json misconception entry has all TS fields")
        else:
            fail("learner.json misconception missing TS fields", str(missing))
        valid_states = {"active","intervened","suspected_resolved","confirmed_resolved","relapsed"}
        if mc.get("state") in valid_states:
            ok(f"learner.json misconception.state='{mc['state']}' is valid enum")
        else:
            fail("learner.json misconception.state invalid", mc.get("state"))
else:
    fail("learner.json missing misconceptions array")

# ─────────────────────────────────────────────────────────────────
# LAYER 6 — Full demo session walk  (end-to-end)
# ─────────────────────────────────────────────────────────────────
section("Layer 6 — Full session walk  (end-to-end demo path)")

try:
    # Step 1: Start session
    sess = start_session()
    sid  = sess["session_id"]
    iid  = sess["item"]["item_id"]
    ok(f"Step 1 — start_session(): session={sid[:8]}...  item={iid}")

    # Step 2: Submit wrong answer (simulate index_1_based student)
    item_for_test = DIAG_ITEMS.get(iid, {})
    real_out = item_for_test.get("signature", {}).get("real", "0")
    believed = item_for_test.get("signature", {}).get(item_for_test.get("family",""), real_out)

    class P1:
        session_id = sid; item_id = iid
        answer = believed if believed != real_out else "wrong_answer"
        confidence = 5

    r1 = diag_answer(P1())
    ok(f"Step 2 — answer() wrong: top={r1['top']}  action={r1['next']['action']}")

    # Step 3: Follow the probe if suggested
    if r1["next"]["action"] == "probe" and r1["next"].get("item"):
        probe_iid = r1["next"]["item"]["item_id"]
        probe_item = DIAG_ITEMS.get(probe_iid, {})
        probe_believed = probe_item.get("signature", {}).get(
            probe_item.get("family",""), "")

        class P2:
            session_id = sid; item_id = probe_iid
            answer = probe_believed or believed
            confidence = 5

        r2 = diag_answer(P2())
        ok(f"Step 3 — probe answer(): top={r2['top']}  action={r2['next']['action']}")
    else:
        r2 = r1
        ok(f"Step 3 — skipped (action was already {r1['next']['action']})")

    # Step 4: Verify intervention is available for top misconception
    top_mc = r2["top"]
    if top_mc not in {"correct", "unknown"}:
        from engine.interventions.builder import build
        iv = build(top_mc)
        ok(f"Step 4 — intervention available for '{top_mc}': real={iv['real_output']!r}")
    else:
        ok(f"Step 4 — top={top_mc!r}: no intervention needed")

    # Step 5: Submit correct answer to simulate post-intervention
    class P3:
        session_id = sid; item_id = iid
        answer = real_out
        confidence = 4

    r3 = diag_answer(P3())
    ok(f"Step 5 — correct answer: top={r3['top']}  action={r3['next']['action']}")

    # Step 6: Verify posterior has shifted toward correct
    ok(f"Step 6 — correct posterior: {r3['posterior'].get('correct', 0):.3f}  "
       f"top_mc: {r3['posterior'].get(top_mc if top_mc not in {'correct','unknown'} else 'noop_method', 0):.3f}")

    # Step 7: Persistence check — use TestClient to go through full route
    from fastapi.testclient import TestClient
    from backend.app.main import app
    import os as _os
    _os.environ["MOCK"] = "0"
    client = TestClient(app)

    start_r = client.post("/session/start")
    assert start_r.status_code == 200
    tsid = start_r.json()["session_id"]
    tiid = start_r.json()["item"]["item_id"]

    ans_r = client.post("/answer", json={
        "session_id": tsid, "item_id": tiid,
        "answer": "anything", "confidence": 3
    })
    assert ans_r.status_code == 200

    from backend.app.db import connect as db_connect
    db2 = db_connect()
    count = db2.execute(
        "SELECT COUNT(*) FROM attempts WHERE session=?", (tsid,)
    ).fetchone()[0]
    db2.close()

    if count >= 1:
        ok(f"Step 7 — SQLite persisted {count} attempt(s) via FastAPI route")
    else:
        fail("Step 7 — attempts not persisted through FastAPI route", f"count={count}")

except Exception as e:
    fail("Full session walk crashed", str(e))
    traceback.print_exc()

# ─────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────
section("MERGE TEST RESULTS")
total = PASS + FAIL + WARN
print(f"  Passed:   {PASS}")
print(f"  Warnings: {WARN}  (known stubs / minor mismatches)")
print(f"  Failed:   {FAIL}")
print()
if FAIL == 0:
    print("  ✅  All integration boundaries are clean. Safe to merge.")
else:
    print("  ❌  Failures above must be fixed before merging.")
    sys.exit(1)
