from .nodes import FuncNode, CallNode, PrintNode, StringNode, BinOpNode
from .errors import AmatakRuntimeError

class Interpreter:
    def __init__(self, tree):
        """Initialize interpreter with AST and setup execution environment"""
        self.tree = tree
        self.functions = {}  # Stores function definitions
        self.variables = {}   # Stores variables

    def interpret(self):
        """Execute the AST and handle runtime errors"""
        print("\n=== INTERPRETER START ===")
        for node in self.tree:
            print(f"Executing: {node}")
            try:
                result = self.visit(node)
                if result is not None:
                    print(f"  -> Returned: {result}")
            except AmatakRuntimeError as e:
                print(f"! Runtime Error executing {node}: {e}")
            except Exception as e:
                print(f"! Unexpected Error executing {node}: {e}")

    def visit(self, node):
        """Dispatch to appropriate visit method based on node type"""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Handle unknown node types"""
        raise AmatakRuntimeError(f"No visit method for {type(node).__name__}")

    def visit_PrintNode(self, node):
        """Execute print statements"""
        value = self.visit(node.value)
        print(value)
        return value

    def visit_StringNode(self, node):
        """Return string literal value"""
        return node.value

    def visit_ArrayNode(self, node):
        """Evaluate array elements"""
        return [self.visit(element) for element in node.elements]

    def visit_ArrayAccessNode(self, node):
        """Handle array indexing with bounds checking"""
        array = self.visit(node.array)
        index = self.visit(node.index)
        try:
            return array[index]
        except IndexError:
            raise AmatakRuntimeError(f"Array index {index} out of bounds")

    def visit_ArrayAssignNode(self, node):
        """Handle array element assignment"""
        array = self.visit(node.array)
        index = self.visit(node.index)
        value = self.visit(node.value)
        array[index] = value
        return value

    def visit_ArrayMethodNode(self, node):
        """Handle array methods (push/pop)"""
        array = self.visit(node.array)
        if node.method == 'push':
            array.append(self.visit(node.args[0]))
        elif node.method == 'pop':
            return array.pop()
        else:
            raise AmatakRuntimeError(f"Unknown array method: {node.method}")

    def visit_ForNode(self, node):
        """Execute for loops"""
        self.variables[node.var_name] = self.visit(node.start)
        while self.variables[node.var_name] < self.visit(node.end):
            for stmt in node.body:
                self.visit(stmt)
            self.variables[node.var_name] += self.visit(node.step)

    def visit_FunctionCallNode(self, node):
        """Handle function calls"""
        if node.name == 'len':
            if len(node.args) != 1:
                raise AmatakRuntimeError("len() expects exactly 1 argument")
            return len(self.visit(node.args[0]))
        elif node.name in self.functions:
            func = self.functions[node.name]
            # TODO: Add parameter handling
            for stmt in func.body:
                self.visit(stmt)
        else:
            raise AmatakRuntimeError(f"Function '{node.name}' not defined")

    def evaluate(self, node):
        """Evaluate expressions to their values"""
        if isinstance(node, StringNode):
            return node.value
        elif isinstance(node, BinOpNode):
            left = self.evaluate(node.left)
            right = self.evaluate(node.right)
            if node.op == "+":
                return str(left) + str(right)
            raise AmatakRuntimeError(f"Unsupported operator: {node.op}")
        raise AmatakRuntimeError(f"Unknown node type: {type(node).__name__}")