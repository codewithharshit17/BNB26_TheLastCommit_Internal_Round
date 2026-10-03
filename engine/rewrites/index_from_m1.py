import ast
class IndexStartsAtMinus1(ast.NodeTransformer):
    def visit_Subscript(self, node):
        self.generic_visit(node)
        if not isinstance(node.slice, ast.Slice):
            node.slice = ast.BinOp(node.slice, ast.Add(), ast.Constant(1))
        return node
