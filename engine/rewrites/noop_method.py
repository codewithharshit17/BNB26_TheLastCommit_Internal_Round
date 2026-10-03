import ast

class NoOpMethodAssigned(ast.NodeTransformer):
    METHODS = {"upper", "lower", "strip", "replace", "split"}
    def visit_Expr(self, node):
        value = node.value
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Attribute) and value.func.attr in self.METHODS and isinstance(value.func.value, ast.Name):
            return ast.copy_location(ast.Assign(targets=[ast.Name(value.func.value.id, ast.Store())], value=value), node)
        if isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in ("sorted", "int") and len(value.args) == 1 and isinstance(value.args[0], ast.Name):
            return ast.copy_location(ast.Assign(targets=[ast.Name(value.args[0].id, ast.Store())], value=value), node)
        return node
