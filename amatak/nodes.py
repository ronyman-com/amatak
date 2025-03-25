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




# Add these to your existing nodes.py

from abc import ABC, abstractmethod
from typing import List, Optional, Union

class Node(ABC):
    """Base class for all AST nodes"""
    @abstractmethod
    def accept(self, visitor):
        pass

class Expr(Node):
    """Base class for all expression nodes"""
    pass

class Stmt(Node):
    """Base class for all statement nodes"""
    pass

# Expression Nodes
class Literal(Expr):
    def __init__(self, value):
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_literal_expr(self)

class Binary(Expr):
    def __init__(self, left: Expr, operator, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_binary_expr(self)

class UnaryOpNode(Expr):
    def __init__(self, op, operand: Expr):
        self.op = op
        self.operand = operand
    
    def accept(self, visitor):
        return visitor.visit_unary_op_expr(self)

class Variable(Expr):
    def __init__(self, name):
        self.name = name
    
    def accept(self, visitor):
        return visitor.visit_variable_expr(self)

class Call(Expr):
    def __init__(self, callee: Expr, args: List[Expr]):
        self.callee = callee
        self.args = args
    
    def accept(self, visitor):
        return visitor.visit_call_expr(self)

class ArrayAccess(Expr):
    def __init__(self, array: Expr, index: Expr):
        self.array = array
        self.index = index
    
    def accept(self, visitor):
        return visitor.visit_array_access_expr(self)

# Statement Nodes
class Expression(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_expression_stmt(self)

class Print(Stmt):
    def __init__(self, expression: Expr):
        self.expression = expression
    
    def accept(self, visitor):
        return visitor.visit_print_stmt(self)

class Var(Stmt):
    def __init__(self, name, initializer: Optional[Expr]):
        self.name = name
        self.initializer = initializer
    
    def accept(self, visitor):
        return visitor.visit_var_stmt(self)

class Block(Stmt):
    def __init__(self, statements: List[Stmt]):
        self.statements = statements
    
    def accept(self, visitor):
        return visitor.visit_block_stmt(self)

class If(Stmt):
    def __init__(self, condition: Expr, then_branch: Stmt, else_branch: Optional[Stmt] = None):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    
    def accept(self, visitor):
        return visitor.visit_if_stmt(self)

class While(Stmt):
    def __init__(self, condition: Expr, body: Stmt):
        self.condition = condition
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_while_stmt(self)

class Function(Stmt):
    def __init__(self, name, params: List[str], body: List[Stmt]):
        self.name = name
        self.params = params
        self.body = body
    
    def accept(self, visitor):
        return visitor.visit_function_stmt(self)

class Return(Stmt):
    def __init__(self, keyword, value: Optional[Expr]):
        self.keyword = keyword
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_return_stmt(self)

# Additional Nodes
class ArrayLiteral(Expr):
    def __init__(self, elements: List[Expr]):
        self.elements = elements
    
    def accept(self, visitor):
        return visitor.visit_array_literal_expr(self)

class Assignment(Expr):
    def __init__(self, name, value: Expr):
        self.name = name
        self.value = value
    
    def accept(self, visitor):
        return visitor.visit_assignment_expr(self)

class Logical(Expr):
    def __init__(self, left: Expr, operator, right: Expr):
        self.left = left
        self.operator = operator
        self.right = right
    
    def accept(self, visitor):
        return visitor.visit_logical_expr(self)