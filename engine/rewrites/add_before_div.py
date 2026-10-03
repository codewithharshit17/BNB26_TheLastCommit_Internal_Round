import ast
class PlusBeforeDiv(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, (ast.Add, ast.Sub)) and isinstance(node.right, ast.BinOp) and isinstance(node.right.op, (ast.Div, ast.Mult)):
            return ast.BinOp(ast.BinOp(node.left, node.op, node.right.left), node.right.op, node.right.right)
        return node
