"""Live end-to-end API test — walks through a full session against the running server."""
import json, sys
import urllib.request, urllib.error

BASE = "http://localhost:8001"
PASS = 0; FAIL = 0

def check(label, cond, got=""):
    global PASS, FAIL
    if cond:
        print(f"  [OK]  {label}")
        PASS += 1
    else:
        print(f"  [FAIL] {label}  =>  {got}")
        FAIL += 1

def get(path):
    with urllib.request.urlopen(f"{BASE}{path}") as r:
        return json.loads(r.read())

def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{BASE}{path}", data=data,
                                  headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

print("\n=== 1. Health ===")
h = get("/health")
check("ok=true", h.get("ok") is True, h)

print("\n=== 2. Start session ===")
s = post("/session/start", {})
check("has session_id",  "session_id" in s, s)
check("has item",        "item" in s, s)
check("item has item_id","item_id" in s["item"], s["item"])
check("item has code",   "code" in s["item"], s["item"])
check("item has kind",   s["item"]["kind"] in ["diagnostic","probe","transfer","discriminator","retest"], s["item"])
sid   = s["session_id"]
iid   = s["item"]["item_id"]
print(f"  session_id: {sid[:16]}...")
print(f"  item_id:    {iid}  kind={s['item']['kind']}  family={s['item']['family']}")

print("\n=== 3. Submit wrong answer (high confidence) ===")
# Send '10' — the index_1_based believed output for a[1] on [10,20,30]
r = post("/answer", {"session_id": sid, "item_id": iid, "answer": "10", "confidence": 5})
check("has posterior",       "posterior" in r, r)
check("has top",             "top" in r, r)
check("has bank_ids (list)", isinstance(r.get("bank_ids"), list), r)
check("has real_output",     "real_output" in r, r)
check("has believed_output", "believed_output" in r, r)
check("has believed_source", "believed_source" in r, r)
check("has next.action",     "action" in r.get("next", {}), r)
post_sum = round(sum(r["posterior"].values()), 6)
check("posterior sums to 1", post_sum == 1.0, post_sum)
print(f"  top={r['top']}  next_action={r['next']['action']}")
print(f"  real={r['real_output']!r}  believed={r['believed_output']!r}")
print(f"  posterior (top 3):", sorted(r["posterior"].items(), key=lambda x: -x[1])[:3])

print("\n=== 4. Submit correct answer ===")
# Use same item, answer the real output
r2 = post("/answer", {"session_id": sid, "item_id": iid,
                       "answer": r["real_output"], "confidence": 4})
check("posterior still sums to 1", round(sum(r2["posterior"].values()), 6) == 1.0)
print(f"  top={r2['top']}  next_action={r2['next']['action']}")

print("\n=== 5. Intervention endpoints ===")
for mid in ["noop_method", "range_1_to_n", "index_1_based", "assign_copies", "add_before_div"]:
    try:
        iv = get(f"/intervention/{mid}")
        check(f"{mid}: has title",           bool(iv.get("title")))
        check(f"{mid}: has steps (3)",       len(iv.get("steps",[])) == 3)
        check(f"{mid}: real != believed",    iv["real_output"] != iv["believed_output"])
    except Exception as e:
        check(f"{mid}: GET /intervention/{mid}", False, str(e))

# Unknown id should 404
print("\n=== 6. Unknown intervention → 404 ===")
try:
    get("/intervention/made_up")
    check("404 on unknown id", False, "no error raised")
except urllib.error.HTTPError as e:
    check("404 on unknown id", e.code == 404, e.code)

print(f"\n{'='*50}")
print(f"  Passed: {PASS}/{PASS+FAIL}")
if FAIL:
    print(f"  Failed: {FAIL}/{PASS+FAIL}")
    sys.exit(1)
else:
    print("  All live API checks passed!")
