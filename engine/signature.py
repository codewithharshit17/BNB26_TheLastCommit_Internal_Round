import ast
from .rewrites import REGISTRY
from .sandbox import run

def believed_source(src, mid):
    entry = next(item for item in REGISTRY if item["id"] == mid)
    tree = entry["transformer"]().visit(ast.parse(src))
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)

def signature(src):
    output = {"real": run(src)}
    for entry in REGISTRY:
        try:
            output[entry["id"]] = run(believed_source(src, entry["id"]))
        except Exception:
            output[entry["id"]] = "RewriteError"
    return output
