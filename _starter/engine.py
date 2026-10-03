import ast, copy, io, contextlib, multiprocessing as mp

# ---------- believed-program rewrites ----------
class NoOpMethodAssigned(ast.NodeTransformer):
    """Bank ids 6-10, 34, 36: student believes str.upper()/lower()/strip()/replace()/split()/sorted() mutate in place.
    `name.upper()` as a bare statement -> `name = name.upper()`"""
    METHODS = {"upper","lower","strip","replace","split"}
    def visit_Expr(self, node):
        v = node.value
        if isinstance(v, ast.Call) and isinstance(v.func, ast.Attribute) \
           and v.func.attr in self.METHODS and isinstance(v.func.value, ast.Name):
            return ast.copy_location(ast.Assign(targets=[ast.Name(v.func.value.id, ast.Store())], value=v), node)
        # sorted(x) as a bare statement -> x = sorted(x)
        if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id in ("sorted","int") \
           and len(v.args) == 1 and isinstance(v.args[0], ast.Name):
            return ast.copy_location(ast.Assign(targets=[ast.Name(v.args[0].id, ast.Store())], value=v), node)
        return node

class RangeOneToN(ast.NodeTransformer):
    """Bank id 1: range(n) believed to give 1..n  ->  range(1, n+1)"""
    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == "range" and len(node.args) == 1:
            node.args = [ast.Constant(1), ast.BinOp(node.args[0], ast.Add(), ast.Constant(1))]
        return node

class Index1Based(ast.NodeTransformer):
    """Bank ids 15, 66: first element is at index 1  ->  a[i] means a[i-1]"""
    def visit_Subscript(self, node):
        self.generic_visit(node)
        if not isinstance(node.slice, ast.Slice):
            node.slice = ast.BinOp(node.slice, ast.Sub(), ast.Constant(1))
        return node

class IndexStartsAtMinus1(ast.NodeTransformer):
    """Bank id 60 (out-of-domain): -1 is first, 0 is second  ->  a[i] means a[i+1]"""
    def visit_Subscript(self, node):
        self.generic_visit(node)
        if not isinstance(node.slice, ast.Slice):
            node.slice = ast.BinOp(node.slice, ast.Add(), ast.Constant(1))
        return node

class AssignmentCopies(ast.NodeTransformer):
    """Bank ids 13, 55: `b = a` makes an independent copy  ->  b = _cp(a)"""
    def visit_Assign(self, node):
        if isinstance(node.value, ast.Name) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            node.value = ast.Call(ast.Name("_cp", ast.Load()), [node.value], [])
        return node

class PlusBeforeDiv(ast.NodeTransformer):
    """Bank ids 63/64: a + b / c believed to be (a + b) / c"""
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, (ast.Add, ast.Sub)) and isinstance(node.right, ast.BinOp) \
           and isinstance(node.right.op, (ast.Div, ast.Mult)):
            inner = ast.BinOp(node.left, node.op, node.right.left)
            return ast.BinOp(inner, node.right.op, node.right.right)
        return node

MISCONCEPTIONS = {
    "noop_method":   NoOpMethodAssigned,
    "range_1_to_n":  RangeOneToN,
    "index_1_based": Index1Based,
    "index_from_m1": IndexStartsAtMinus1,
    "assign_copies": AssignmentCopies,
    "add_before_div":PlusBeforeDiv,
}

def believed_source(src, mid):
    tree = ast.parse(src)
    tree = MISCONCEPTIONS[mid]().visit(tree)
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)

# ---------- sandboxed execution ----------
SAFE = {k: __builtins__.__dict__[k] if hasattr(__builtins__, "__dict__") else __builtins__[k]
        for k in ["print","range","len","sorted","int","str","float","list","dict","set","tuple","sum","min","max","abs","enumerate","zip","bool","reversed","isinstance"]}
BANNED = (ast.Import, ast.ImportFrom, ast.Global) 

def _worker(src, q):
    try:
        tree = ast.parse(src)
        for n in ast.walk(tree):
            if isinstance(n, (ast.Import, ast.ImportFrom)) or (isinstance(n, ast.Attribute) and n.attr.startswith("__")):
                q.put("SecurityError"); return
        buf = io.StringIO()
        env = {"__builtins__": SAFE, "_cp": copy.copy}
        with contextlib.redirect_stdout(buf):
            exec(compile(tree, "<student>", "exec"), env)
        q.put(buf.getvalue().strip())
    except Exception as e:
        q.put(type(e).__name__)

def run(src, timeout=2):
    q = mp.Queue(); p = mp.Process(target=_worker, args=(src, q)); p.start(); p.join(timeout)
    if p.is_alive(): p.kill(); return "Timeout"
    return q.get() if not q.empty() else "NoOutput"

def signature(src):
    out = {"real": run(src)}
    for m in MISCONCEPTIONS:
        try: out[m] = run(believed_source(src, m))
        except Exception as e: out[m] = "RewriteError"
    return out
