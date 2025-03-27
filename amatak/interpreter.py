from .nodes import FuncNode, CallNode, PrintNode, StringNode, BinOpNode
from .errors import AmatakRuntimeError
from .tokens import TokenType 

class Context:
    """Runtime context for variable storage and scope management"""
    def __init__(self, parent=None):
        self.parent = parent
        self.variables = {}
        self.functions = {}

    def set(self, name, value):
        """Set a variable or function in the current context"""
        self.variables[name] = value

    def get(self, name):
        """Get a variable from the current or parent context"""
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise AmatakRuntimeError(f"Undefined variable: '{name}'")

class Interpreter:
    def __init__(self, tree, debug=False, context=None):
        """Initialize interpreter with AST and setup execution environment"""
        self.tree = tree
        self.context = context if context else Context()
        self.debug = debug

    def interpret(self):
        """Execute the AST with error handling and debug output"""
        if self.debug:
            print("\n=== INTERPRETER START ===")
        
        try:
            for node in self.tree:
                if self.debug:
                    print(f"Executing: {node}")
                
                result = self.visit(node)
                
                if self.debug and result is not None:
                    print(f"  -> Returned: {result}")
                    
        except AmatakRuntimeError as e:
            if self.debug:
                print(f"! Runtime Error executing {node}: {e}", file=sys.stderr)
            raise
        except Exception as e:
            if self.debug:
                print(f"! Unexpected Error executing {node}: {e}", file=sys.stderr)
            raise

    def visit(self, node):
        """Dispatch to appropriate visit method based on node type"""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Handle unknown node types"""
        raise AmatakRuntimeError(f"No visit method for {type(node).__name__}")

    def visit_NumberNode(self, node):
        """Handle numeric literals"""
        try:
            return float(node.value) if '.' in node.value else int(node.value)
        except ValueError:
            raise AmatakRuntimeError(f"Invalid number: {node.value}")

    def visit_PrintNode(self, node):
        """Execute print statements with forced flushing"""
        value = self.visit(node.value)
        print(str(value), flush=True)  # Convert to string and force flush
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
        
        # In interpreter.py
    def visit_BinOpNode(self, node):
        """Handle binary operations with type conversion for string concatenation"""
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        # Convert numbers to strings when concatenating with strings
        if node.op == TokenType.PLUS:
            if isinstance(left, str) or isinstance(right, str):
                return str(left) + str(right)
            return left + right
        
        # Preserve all existing numeric operations
        elif node.op == TokenType.MINUS:
            return left - right
        elif node.op == TokenType.MUL:
            return left * right
        elif node.op == TokenType.DIV:
            return left / right
        elif node.op == TokenType.MOD:
            return left % right
        elif node.op == TokenType.LT:
            return left < right
        elif node.op == TokenType.GT:
            return left > right
        elif node.op == TokenType.LTE:
            return left <= right
        elif node.op == TokenType.GTE:
            return left >= right
        elif node.op == TokenType.EQ:
            return left == right
        elif node.op == TokenType.NEQ:
            return left != right
        else:
            raise AmatakRuntimeError(f"Unknown operator: {node.op}")

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
    

    # In interpreter.py
    def visit_TernaryNode(self, node):
        condition = self.visit(node.condition)
        if condition:
            return self.visit(node.true_expr)
        else:
            return self.visit(node.false_expr)