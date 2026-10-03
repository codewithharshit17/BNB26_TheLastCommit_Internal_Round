import ast
class Index1Based(ast.NodeTransformer):
    def visit_Subscript(self, node):
        self.generic_visit(node)
        if not isinstance(node.slice, ast.Slice):
            node.slice = ast.BinOp(node.slice, ast.Sub(), ast.Constant(1))
        return node
