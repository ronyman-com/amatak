

class ASTNode:
    pass

class PrintNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"PrintNode({self.value})"

class StringNode(ASTNode):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"StringNode({self.value})"

class ASTNode:
    """Base class for all Abstract Syntax Tree nodes."""
    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{self.__class__.__name__}({attrs})"

class FuncNode(ASTNode):
    """Function definition node."""
    def __init__(self, name, params, body):
        """
        Args:
            name: Function name (str)
            params: List of parameter names (list[str])
            body: List of statements in function body (list[ASTNode])
        """
        self.name = name
        self.params = params
        self.body = body

class CallNode(ASTNode):
    """Function call node."""
    def __init__(self, name, args):
        """
        Args:
            name: Function name to call (str)
            args: List of argument nodes (list[ASTNode])
        """
        self.name = name
        self.args = args

class PrintNode(ASTNode):
    """Print statement node."""
    def __init__(self, value):
        """
        Args:
            value: Expression to print (ASTNode)
        """
        self.value = value

class StringNode(ASTNode):
    """String literal node."""
    def __init__(self, value):
        """
        Args:
            value: String value (str)
        """
        self.value = value

class BinOpNode(ASTNode):
    """Binary operation node."""
    def __init__(self, left, op, right):
        """
        Args:
            left: Left operand (ASTNode)
            op: Operator (str)
            right: Right operand (ASTNode)
        """
        self.left = left
        self.op = op
        self.right = right

class NumberNode(ASTNode):
    """Numeric literal node."""
    def __init__(self, value):
        """
        Args:
            value: Numeric value (int|float)
        """
        self.value = value

class IdentifierNode(ASTNode):
    """Variable identifier node."""
    def __init__(self, name):
        """
        Args:
            name: Variable name (str)
        """
        self.name = name