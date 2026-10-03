import ast
class RangeOneToN(ast.NodeTransformer):
    def visit_Call(self, node):
        self.generic_visit(node)
        if isinstance(node.func, ast.Name) and node.func.id == "range" and len(node.args) == 1:
            node.args = [ast.Constant(1), ast.BinOp(node.args[0], ast.Add(), ast.Constant(1))]
        return node
