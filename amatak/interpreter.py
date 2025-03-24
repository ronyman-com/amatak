from .nodes import FuncNode, CallNode, PrintNode, StringNode, BinOpNode
from .errors import AmatakRuntimeError

class Interpreter:
    def __init__(self, tree):
        self.tree = tree
        self.functions = {}
        self.variables = {}
        self.variables = {}
        for node in self.tree:
            self.visit(node)

    # In interpreter.py, modify interpret():
    def interpret(self):
        print("\n=== INTERPRETER START ===")
        for node in self.tree:
            print(f"Executing: {node}")
            try:
                result = self.visit(node)
                if result is not None:
                    print(f"  -> Returned: {result}")
            except Exception as e:
                print(f"! Error executing {node}: {e}")

    def generic_visit(self, node):
        """Fallback method for unknown node types"""
        raise NotImplementedError(f"No visit method for {type(node).__name__}")
    def visit_PrintNode(self, node):
        """Handle print statements"""
        value = self.visit(node.value)
        print(value)

    def visit_StringNode(self, node):
        """Handle string literals"""
        return node.value

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def visit_ArrayNode(self, node):
        return [self.visit(element) for element in node.elements]

    def visit_ArrayAccessNode(self, node):
        array = self.visit(node.array)
        index = self.visit(node.index)
        return array[index]

    def visit_ArrayAssignNode(self, node):
        array = self.visit(node.array)
        index = self.visit(node.index)
        value = self.visit(node.value)
        array[index] = value

    def visit_ArrayMethodNode(self, node):
        array = self.visit(node.array)
        if node.method == 'push':
            value = self.visit(node.args[0])
            array.append(value)
        elif node.method == 'pop':
            return array.pop()

    def visit_ForNode(self, node):
        self.variables[node.var_name] = self.visit(node.start)
        while self.variables[node.var_name] < self.visit(node.end):
            for stmt in node.body:
                self.visit(stmt)
            self.variables[node.var_name] += self.visit(node.step)

    def evaluate(self, node):
        """Evaluate AST nodes to their values"""
        if hasattr(node, 'value'):  # For StringNode, NumberNode, etc.
            return node.value
        # Add more evaluation cases as needed
        raise NotImplementedError(f"Cannot evaluate {type(node).__name__}")

    def execute_call(self, node):
        if node.name not in self.functions:
            raise AmatakRuntimeError(f"Function '{node.name}' not defined")
        
        func = self.functions[node.name]
        # TODO: Add parameter handling
        for stmt in func.body:
            self.execute_statement(stmt)

    def execute_statement(self, node):
        if isinstance(node, PrintNode):
            value = self.evaluate(node.value)
            print(value)

    def evaluate(self, node):
        if isinstance(node, StringNode):
            return node.value
        elif isinstance(node, BinOpNode):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == "+":
                return str(left) + str(right)
            raise AmatakRuntimeError(f"Unsupported operator: {node.op}")
        raise AmatakRuntimeError(f"Unknown node type: {type(node).__name__}")
    



