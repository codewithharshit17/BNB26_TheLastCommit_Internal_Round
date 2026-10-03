"""Sandboxed Python execution for Re:Learn.

Two execution modes
-------------------
run_inprocess(src, timeout)
    Executes in a daemon thread.  Fast and Windows-safe (no spawn).
    Cannot kill CPU-bound infinite loops — the GIL is held by a tight
    Python loop and the thread cannot be preempted.
    Used by the item generator and signature helper (our own trusted code).

run_subprocess(src, timeout)
    Executes in a separate OS process via multiprocessing spawn.
    Correctly kills infinite loops with process.kill().
    Must only be called from a properly guarded entry-point (uvicorn/pytest
    main guard), never at module import time on Windows.

run(src, timeout)
    Public API.  Chooses the right backend automatically:
      - If env var RELEARN_SANDBOX=subprocess → run_subprocess (API path)
      - Otherwise                             → run_inprocess  (generator/eval path)

    The FastAPI server sets RELEARN_SANDBOX=subprocess at startup so all
    live student answers go through the subprocess path.

Security check (shared)
    Blocks imports and dunder attribute access before exec.
    Caps output at 4 KB.
"""

from __future__ import annotations

import ast
import contextlib
import copy
import io
import os
import threading
from typing import Optional

try:
    import resource  # Linux / macOS only
except ImportError:  # pragma: no cover - Windows
    resource = None

# ---------------------------------------------------------------------------
# Safe builtins
# ---------------------------------------------------------------------------

_BUILTIN_NAMES = [
    "print", "range", "len", "sorted", "int", "str", "float",
    "list", "dict", "set", "tuple", "sum", "min", "max", "abs",
    "enumerate", "zip", "bool", "reversed", "isinstance",
]
_builtins_src = __builtins__.__dict__ if hasattr(__builtins__, "__dict__") else __builtins__
SAFE: dict = {name: _builtins_src[name] for name in _BUILTIN_NAMES}

_MAX_OUTPUT = 4096  # chars


# ---------------------------------------------------------------------------
# Security check
# ---------------------------------------------------------------------------

def _security_check(src: str) -> Optional[str]:
    """Return an error string if *src* is unsafe, else None."""
    try:
        tree = ast.parse(src)
    except SyntaxError as exc:
        return f"SyntaxError: {exc}"
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            return "SecurityError"
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            return "SecurityError"
    return None


# ---------------------------------------------------------------------------
# In-process runner (threading-based timeout)
# ---------------------------------------------------------------------------

def run_inprocess(src: str, timeout: float = 2.0) -> str:
    """Execute *src* in a daemon thread with a threading-based timeout.

    Caveat: a tight ``while True: pass`` loop holds the GIL and cannot be
    interrupted.  Use ``run_subprocess`` for untrusted live student code.
    Safe for our own trusted AST-rewritten snippets (item generator, eval).
    """
    err = _security_check(src)
    if err:
        return err

    result: list[str] = []

    def _target() -> None:
        try:
            tree = ast.parse(src)
            buf = io.StringIO()
            env: dict = {"__builtins__": SAFE, "_cp": copy.copy}
            with contextlib.redirect_stdout(buf):
                exec(compile(tree, "<student>", "exec"), env)  # noqa: S102
            result.append(buf.getvalue().strip()[:_MAX_OUTPUT])
        except Exception as exc:
            result.append(type(exc).__name__)

    t = threading.Thread(target=_target, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        return "Timeout"
    return result[0] if result else "NoOutput"


# ---------------------------------------------------------------------------
# Subprocess worker — module-level for pickle on Windows spawn
# ---------------------------------------------------------------------------

def _worker(src: str, q) -> None:  # pragma: no cover
    """Run in the child process.  Reuses run_inprocess (security check +
    exec) so all safety logic lives in one place."""
    if resource is not None:
        try:
            resource.setrlimit(
                resource.RLIMIT_AS,
                (256 * 1024 * 1024, 256 * 1024 * 1024)
            )
        except Exception:
            pass
    q.put(run_inprocess(src))


# ---------------------------------------------------------------------------
# Subprocess runner (process-level timeout)
# ---------------------------------------------------------------------------

def run_subprocess(src: str, timeout: float = 2.0) -> str:  # pragma: no cover
    """Execute *src* in a separate OS process.

    Correctly kills CPU-bound infinite loops via ``process.kill()``.

    WARNING: Do NOT call at module import time or from scripts without a
    ``if __name__ == '__main__':`` guard on Windows — the spawn start method
    will cause a recursive import deadlock.
    """
    import multiprocessing as mp  # local import — keeps module-level clean
    ctx = mp.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_worker, args=(src, q))
    p.start()
    p.join(timeout)
    if p.is_alive():
        p.kill()
        p.join()
        return "Timeout"
    return q.get() if not q.empty() else "NoOutput"


# ---------------------------------------------------------------------------
# Public API — auto-selects backend
# ---------------------------------------------------------------------------

def run(src: str, timeout: float = 2.0) -> str:
    """Execute *src* safely and return its stdout output.

    Backend selection (set env var before starting uvicorn):
        RELEARN_SANDBOX=subprocess  →  run_subprocess  (API / live student code)
        (default)                   →  run_inprocess   (generator / eval)

    Returns one of:
        stdout text (stripped, capped at 4 KB)
        exception class name e.g. "NameError"
        "Timeout"
        "SecurityError"
        "NoOutput"
        "SyntaxError: <msg>"
    """
    if os.environ.get("RELEARN_SANDBOX") == "subprocess":
        return run_subprocess(src, timeout)  # pragma: no cover
    return run_inprocess(src, timeout)
