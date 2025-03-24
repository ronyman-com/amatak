from .nodes import FuncNode, CallNode, PrintNode, StringNode, BinOpNode
from .errors import AmatakRuntimeError

class Interpreter:
    def __init__(self, tree):
        self.tree = tree
        self.functions = {}
        self.variables = {}

    def interpret(self):
        for node in self.tree:
            if isinstance(node, PrintNode):
                # Evaluate the expression inside the print statement
                value = self.evaluate(node.value)
                print(value)

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
    



    

