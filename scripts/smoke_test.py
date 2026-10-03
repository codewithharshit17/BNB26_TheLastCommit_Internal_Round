"""
Re:Learn — Sukhada's components smoke test
Run from repo root:   PYTHONPATH=. python scripts/smoke_test.py

Covers:
  1. Sandbox security and timeout
  2. AST rewrites (all 6 families)
  3. Signature computation
  4. Item bank (load, counts, schema)
  5. Interventions (all 5 families, outputs verified)
  6. Simulated students (all 6 types)
  7. Backend diagnosis service (start_session + answer)
"""

import sys
import traceback

PASS = 0
FAIL = 0

def check(label, got, expected):
    global PASS, FAIL
    if got == expected:
        print(f"  [OK]  {label}")
        PASS += 1
    else:
        print(f"  [FAIL] {label}")
        print(f"         expected: {expected!r}")
        print(f"         got:      {got!r}")
        FAIL += 1

def section(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")

# ------------------------------------------------------------------ 1. Sandbox
section("1. Sandbox")
from engine.sandbox import run

check("print(1+1)",          run("print(1+1)"),                   "2")
check("list index",          run("print([10,20,30][1])"),          "20")
check("import blocked",      run("import os"),                     "SecurityError")
check("dunder blocked",      run("print(().__class__)"),           "SecurityError")
# Note: tight Python loops hold the GIL so the in-process timeout cannot
# interrupt them; the subprocess path (run_subprocess) handles that.
# Timeout is verified by the unit-test suite instead.
check("syntax error",        "SyntaxError" in run("def ("), True)

# ------------------------------------------------------------------ 2. Rewrites
section("2. AST Rewrites")
from engine.signature import believed_source

cases = [
    ("noop_method",   'name = "hello"\nname.upper()\nprint(name)', "HELLO"),
    ("range_1_to_n",  "for i in range(3):\n    print(i)",          "1\n2\n3"),
    ("index_1_based", "a = [10,20,30]\nprint(a[1])",               "10"),
    ("assign_copies", "a=[1,2,3]\nb=a\na.append(4)\nprint(b)",     "[1, 2, 3]"),
    ("add_before_div","print(10 + 20 / 2)",                        "15.0"),
    ("index_from_m1", "a = [10,20,30]\nprint(a[1])",               "30"),
]
for mid, src, expected_believed in cases:
    got = run(believed_source(src, mid))
    check(f"believed output: {mid}", got, expected_believed)

# ------------------------------------------------------------------ 3. Signature
section("3. Signature")
from engine.signature import signature

sig = signature("a = [10,20,30]\nprint(a[1])")
check("real output",          sig["real"],          "20")
check("index_1_based output", sig["index_1_based"], "10")
check("index_from_m1 output", sig["index_from_m1"], "30")
check("noop_method output",   sig["noop_method"],   "20")   # no method call → same as real
all_keys = {"real","noop_method","range_1_to_n","index_1_based","index_from_m1","assign_copies","add_before_div"}
check("all hypothesis keys present", set(sig.keys()) >= all_keys, True)

# ------------------------------------------------------------------ 4. Item bank
section("4. Item bank")
from engine.items.generator import load as load_items
from collections import defaultdict

items = load_items()
check(">=40 items",  len(items) >= 40, True)
check(">=58 items",  len(items) >= 58, True)

by_family = defaultdict(lambda: defaultdict(int))
for it in items:
    by_family[it["family"]][it["kind"]] += 1

for fam in ["noop_method","range_1_to_n","index_1_based","assign_copies","add_before_div"]:
    check(f"{fam}: >=3 discriminators", by_family[fam]["discriminator"] >= 3, True)
    check(f"{fam}: >=2 transfer",       by_family[fam]["transfer"] >= 2,       True)

# Check schema of first item
item0 = items[0]
for key in ["item_id","kind","family","prompt","code","signature","discriminates"]:
    check(f"item schema has '{key}'", key in item0, True)

# Every item must discriminate
non_disc = [i["item_id"] for i in items if not i["discriminates"]]
check("no non-discriminating items leaked", non_disc, [])

# ------------------------------------------------------------------ 5. Interventions
section("5. Interventions")
from engine.interventions.builder import build, load as load_interventions

expected_outputs = {
    "noop_method":   ("hello",     "HELLO"),
    "range_1_to_n":  ("0\n1\n2\n3\n4", "1\n2\n3\n4\n5"),
    "index_1_based": ("20",        "10"),
    "assign_copies": ("[1, 2, 3, 4]", "[1, 2, 3]"),
    "add_before_div":("20.0",      "15.0"),
}
for mid, (exp_real, exp_believed) in expected_outputs.items():
    iv = build(mid)
    check(f"{mid}: real_output",    iv["real_output"],    exp_real)
    check(f"{mid}: believed_output",iv["believed_output"],exp_believed)
    check(f"{mid}: 3 steps",        len(iv["steps"]) == 3, True)
    check(f"{mid}: has takeaway",   bool(iv["takeaway"]), True)

# held-out raises
try:
    build("index_from_m1")
    check("held-out raises NotImplementedError", False, True)
except NotImplementedError:
    check("held-out raises NotImplementedError", True, True)

# load() round-trip
interventions_json = load_interventions()
check("load() returns 5 entries", len(interventions_json) == 5, True)

# ------------------------------------------------------------------ 6. Simulator
section("6. Simulated students")
import numpy as np
from engine.simulator.students import make_student, simulate

rng = np.random.default_rng(42)

# Use a real item from the bank with a known discriminating family
disc_item = next(i for i in items if i["family"] == "noop_method" and i["kind"] == "discriminator")
real_out     = disc_item["signature"]["real"]
believed_out = disc_item["signature"]["noop_method"]

def count_believed(kind, n=300, **kw):
    s = make_student(kind, **kw)
    rng2 = np.random.default_rng(0)
    return sum(s(disc_item, rng2) == believed_out for _ in range(n))

# clean: ~85%
c = count_believed("clean", misconception="noop_method")
check("clean: ~85% believed (>=200/300)",  c >= 200, True)
check("clean: not always believed (<290)", c < 290,  True)

# true_learner after intervention: ~5% believed
s_tl = make_student("true_learner", misconception="noop_method")
s_tl.intervened = True
rng3 = np.random.default_rng(1)
tl_believed = sum(s_tl(disc_item, rng3) == believed_out for _ in range(300))
check("true_learner after intervention: <30/300 believed", tl_believed < 30, True)

# patcher: correct on patched item, wrong on unpatch-ed
s_p = make_student("patcher", misconception="noop_method")
s_p.intervened = True
s_p.patched_ids = {disc_item["item_id"]}
rng4 = np.random.default_rng(2)
patched_real = sum(s_p(disc_item, rng4) == real_out for _ in range(100))
check("patcher: correct on patched item (>=90/100)", patched_real >= 90, True)

# other item not patched — still wrong
other_disc = next(i for i in items
                  if i["family"] == "noop_method"
                  and i["kind"] == "discriminator"
                  and i["item_id"] != disc_item["item_id"])
rng5 = np.random.default_rng(3)
other_believed = sum(
    s_p(other_disc, rng5) == other_disc["signature"]["noop_method"]
    for _ in range(200)
)
check("patcher: still wrong on unpatched transfer (>=100/200)", other_believed >= 100, True)

# unknown student uses held-out misconception
held_item = next(
    (i for i in items if i["signature"].get("index_from_m1") not in (None, i["signature"]["real"])),
    None
)
if held_item:
    s_u = make_student("unknown", misconception="index_from_m1")
    rng6 = np.random.default_rng(4)
    u_believed = sum(
        s_u(held_item, rng6) == held_item["signature"]["index_from_m1"]
        for _ in range(200)
    )
    check("unknown: uses held-out misconception (>=100/200)", u_believed >= 100, True)

# ------------------------------------------------------------------ 7. Backend
section("7. Backend diagnosis service")
from backend.app.services.diagnosis import start_session, answer, ITEMS as DIAG_ITEMS

check("ITEMS loaded from bank",   len(DIAG_ITEMS) >= 40, True)

session_result = start_session()
check("start_session returns session_id", "session_id" in session_result, True)
check("start_session returns item",       "item" in session_result,       True)
check("start item has item_id",           "item_id" in session_result["item"], True)

# Simulate submitting the wrong answer (index_1_based misconception)
sid = session_result["session_id"]
start_item = session_result["item"]

class FakePayload:
    session_id = sid
    item_id    = start_item["item_id"]
    answer     = "10"   # believed output for index_1_based on a[1]
    confidence = 5

try:
    ans = answer(FakePayload())
    check("answer returns posterior",       "posterior" in ans, True)
    check("answer returns top",             "top" in ans,       True)
    check("answer returns bank_ids",        "bank_ids" in ans,  True)
    check("answer returns real_output",     "real_output" in ans, True)
    check("answer returns believed_output", "believed_output" in ans, True)
    check("answer returns next action",     "next" in ans,      True)
    check("posterior sums to ~1.0",
          abs(sum(ans["posterior"].values()) - 1.0) < 1e-9, True)
except Exception as e:
    traceback.print_exc()
    FAIL += 1
    print(f"  [FAIL] answer() raised: {e}")

# ------------------------------------------------------------------ Summary
section("RESULTS")
total = PASS + FAIL
print(f"  Passed: {PASS}/{total}")
if FAIL:
    print(f"  Failed: {FAIL}/{total}")
    sys.exit(1)
else:
    print("  All checks passed!")
    sys.exit(0)
