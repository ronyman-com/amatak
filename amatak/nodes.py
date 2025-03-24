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

class ArrayNode(ASTNode):
    """Array literal node."""
    def __init__(self, elements):
        """
        Args:
            elements: List of element nodes (list[ASTNode])
        """
        self.elements = elements

class ArrayAccessNode(ASTNode):
    """Array access node."""
    def __init__(self, array, index, value=None):
        """
        Args:
            array: Array expression (ASTNode)
            index: Index expression (ASTNode)
            value: Optional value for assignment (ASTNode)
        """
        self.array = array
        self.index = index
        self.value = value  # Only used for assignments like arr[0] = 5

class AssignmentNode(ASTNode):
    """Variable assignment node."""
    def __init__(self, name, value):
        """
        Args:
            name: Variable name (str or ASTNode for array access)
            value: Expression to assign (ASTNode)
        """
        self.name = name
        self.value = value

class ForNode(ASTNode):
    """For loop node."""
    def __init__(self, var_name, start, condition, step, body):
        """
        Args:
            var_name: Loop variable name (str)
            start: Starting value expression (ASTNode)
            condition: Loop condition expression (ASTNode)
            step: Step expression (ASTNode)
            body: List of statements in loop body (list[ASTNode])
        """
        self.var_name = var_name
        self.start = start
        self.condition = condition
        self.step = step
        self.body = body

class BooleanNode(ASTNode):
    """Boolean literal node."""
    def __init__(self, value):
        """
        Args:
            value: Boolean value (bool)
        """
        self.value = value

class IfNode(ASTNode):
    """If statement node."""
    def __init__(self, condition, then_branch, else_branch=None):
        """
        Args:
            condition: Condition expression (ASTNode)
            then_branch: Statements in then branch (list[ASTNode])
            else_branch: Statements in else branch (list[ASTNode], optional)
        """
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch

class ReturnNode(ASTNode):
    """Return statement node."""
    def __init__(self, expression=None):
        """
        Args:
            expression: Expression to return (ASTNode, optional)
        """
        self.expression = expression