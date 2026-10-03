import ast
class AssignmentCopies(ast.NodeTransformer):
    def visit_Assign(self, node):
        if isinstance(node.value, ast.Name) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            node.value = ast.Call(ast.Name("_cp", ast.Load()), [node.value], [])
        return node
