from abc import ABC, abstractmethod
from ..nodes import *

class ASTVisitor(ABC):
    """Base class for AST visitors"""
    
    @abstractmethod
    def visit(self, node):
        pass
    
    def visit_NumberNode(self, node):
        return node
    
    def visit_StringNode(self, node):
        return node
    
    def visit_IdentifierNode(self, node):
        return node
    
    def visit_BinOpNode(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)
        return BinOpNode(left, node.op, right)
    
    def visit_UnaryOpNode(self, node):
        operand = self.visit(node.operand)
        return UnaryOpNode(node.op, operand)
    
    def visit_AssignmentNode(self, node):
        target = self.visit(node.target)
        value = self.visit(node.value)
        return AssignmentNode(target, value)
    
    def visit_IfNode(self, node):
        condition = self.visit(node.condition)
        then_branch = self.visit(node.then_branch)
        else_branch = self.visit(node.else_branch) if node.else_branch else None
        return IfNode(condition, then_branch, else_branch)
    
    def visit_WhileNode(self, node):
        condition = self.visit(node.condition)
        body = self.visit(node.body)
        return WhileNode(condition, body)
    
    def visit_ForNode(self, node):
        start = self.visit(node.start)
        end = self.visit(node.end)
        step = self.visit(node.step)
        body = [self.visit(stmt) for stmt in node.body]
        return ForNode(node.var_name, start, end, step, body)
    
    def visit_FuncNode(self, node):
        params = node.params
        body = [self.visit(stmt) for stmt in node.body]
        return FuncNode(node.name, params, body)
    
    def visit_CallNode(self, node):
        args = [self.visit(arg) for arg in node.args]
        return CallNode(node.name, args)
    
    def visit_ReturnNode(self, node):
        value = self.visit(node.value) if node.value else None
        return ReturnNode(value)
    
    def visit_ArrayNode(self, node):
        elements = [self.visit(el) for el in node.elements]
        return ArrayNode(elements)
    
    def visit_ArrayAccessNode(self, node):
        array = self.visit(node.array)
        index = self.visit(node.index)
        return ArrayAccessNode(array, index)
    
    def visit_ArrayAssignNode(self, node):
        array = self.visit(node.array)
        index = self.visit(node.index)
        value = self.visit(node.value)
        return ArrayAssignNode(array, index, value)
    
    def visit_BlockNode(self, node):
        statements = [self.visit(stmt) for stmt in node.statements]
        return BlockNode(statements)
    
    def visit_ExpressionNode(self, node):
        expr = self.visit(node.expression)
        return ExpressionNode(expr)
    
    def visit_PrintNode(self, node):
        value = self.visit(node.value)
        return PrintNode(value)
    
    def visit_LambdaNode(self, node):
        params = node.params
        body = self.visit(node.body)
        return LambdaNode(params, body)