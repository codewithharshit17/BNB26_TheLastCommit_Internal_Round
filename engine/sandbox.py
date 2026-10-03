import ast
import contextlib
import copy
import io
import multiprocessing as mp

try:
    import resource
except ImportError:  # pragma: no cover - Windows
    resource = None

_BUILTIN_NAMES = ["print", "range", "len", "sorted", "int", "str", "float", "list", "dict", "set", "tuple", "sum", "min", "max", "abs", "enumerate", "zip", "bool", "reversed", "isinstance"]
_builtins = __builtins__.__dict__ if hasattr(__builtins__, "__dict__") else __builtins__
SAFE = {name: _builtins[name] for name in _BUILTIN_NAMES}


def _worker(src, q):
    try:
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)) or (isinstance(node, ast.Attribute) and node.attr.startswith("__")):
                q.put("SecurityError")
                return
        buf = io.StringIO()
        env = {"__builtins__": SAFE, "_cp": copy.copy}
        with contextlib.redirect_stdout(buf):
            exec(compile(tree, "<student>", "exec"), env)
        q.put(buf.getvalue().strip())
    except Exception as exc:
        q.put(type(exc).__name__)


def run(src, timeout=2):
    q = mp.Queue()
    process = mp.Process(target=_worker, args=(src, q))
    process.start()
    process.join(timeout)
    if process.is_alive():
        process.kill()
        return "Timeout"
    return q.get() if not q.empty() else "NoOutput"
