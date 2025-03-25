from ..nodes import *
from .visitor import ASTVisitor

class ASTOptimizer(ASTVisitor):
    def __init__(self):
        super().__init__()
        self.optimizations = 0

    def optimize(self, node):
        """Entry point for optimization"""
        self.optimizations = 0
        optimized_node = self.visit(node)
        print(f"Performed {self.optimizations} optimizations")
        return optimized_node

    def visit_BinOpNode(self, node):
        # Constant folding for binary operations
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        if isinstance(left, NumberNode) and isinstance(right, NumberNode):
            self.optimizations += 1
            if node.op == '+':
                return NumberNode(left.value + right.value)
            elif node.op == '-':
                return NumberNode(left.value - right.value)
            elif node.op == '*':
                return NumberNode(left.value * right.value)
            elif node.op == '/':
                return NumberNode(left.value / right.value)
            elif node.op == '<':
                return NumberNode(1 if left.value < right.value else 0)
            elif node.op == '>':
                return NumberNode(1 if left.value > right.value else 0)
            elif node.op == '==':
                return NumberNode(1 if left.value == right.value else 0)
        
        return BinOpNode(left, node.op, right)

    def visit_UnaryOpNode(self, node):
        operand = self.visit(node.operand)
        
        if isinstance(operand, NumberNode):
            self.optimizations += 1
            if node.op == '-':
                return NumberNode(-operand.value)
            elif node.op == '!':
                return NumberNode(0 if operand.value else 1)
        
        return UnaryOpNode(node.op, operand)

    def visit_IfNode(self, node):
        condition = self.visit(node.condition)
        
        # Evaluate constant conditions
        if isinstance(condition, NumberNode):
            self.optimizations += 1
            if condition.value:
                return self.visit(node.then_branch)
            elif node.else_branch:
                return self.visit(node.else_branch)
            return None
        
        return IfNode(
            condition,
            self.visit(node.then_branch),
            self.visit(node.else_branch) if node.else_branch else None
        )

    def visit_ForNode(self, node):
        # Optimize loop bounds if they're constants
        start = self.visit(node.start)
        end = self.visit(node.end)
        step = self.visit(node.step)
        
        # If all bounds are constant, we might unroll the loop
        if (isinstance(start, NumberNode) and 
            isinstance(end, NumberNode) and 
            isinstance(step, NumberNode)):
            # Simple case: loop runs zero times
            if (step.value > 0 and start.value >= end.value) or \
               (step.value < 0 and start.value <= end.value):
                self.optimizations +=