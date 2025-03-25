from ..nodes import *
from .visitor import ASTVisitor

class ASTTransformer(ASTVisitor):
    def __init__(self):
        super().__init__()
    
    def transform(self, node):
        """Entry point for AST transformation"""
        return self.visit(node)

    def visit_BinOpNode(self, node):
        # Transform both sides first
        left = self.visit(node.left)
        right = self.visit(node.right)
        
        # Convert relational operators to numerical comparisons
        if node.op in ('<', '>', '<=', '>=', '==', '!='):
            return self._transform_relational_op(left, right, node.op)
        
        return BinOpNode(left, node.op, right)

    def _transform_relational_op(self, left, right, op):
        """Transform relational ops to numerical (0/1) results"""
        comparison = BinOpNode(left, op, right)
        return IfNode(
            comparison,
            NumberNode(1),
            NumberNode(0)
        )

    def visit_ForNode(self, node):
        # Transform for loops into while loops
        init = AssignmentNode(
            IdentifierNode(node.var_name),
            self.visit(node.start)
        )
        
        condition = BinOpNode(
            IdentifierNode(node.var_name),
            '<',
            self.visit(node.end)
        )
        
        increment = AssignmentNode(
            IdentifierNode(node.var_name),
            BinOpNode(
                IdentifierNode(node.var_name),
                '+',
                self.visit(node.step)
            )
        )
        
        # Create while loop body with the original body + increment
        body = node.body.copy()
        body.append(increment)
        
        transformed_body = [self.visit(stmt) for stmt in body]
        
        return BlockNode([
            init,
            WhileNode(condition, BlockNode(transformed_body))
        ])

    def visit_ArrayNode(self, node):
        # Transform array literals into array constructor calls
        elements = [self.visit(el) for el in node.elements]
        
        # For empty arrays, just call the constructor
        if not elements:
            return CallNode('__array__', [])
        
        # For non-empty arrays, create a sequence of push operations
        array_var = IdentifierNode('__temp_array__')
        constructor = CallNode('__array__', [])
        init = AssignmentNode(array_var, constructor)
        
        push_ops = []
        for element in elements:
            push = CallNode(
                '__array_push__',
                [array_var, element]
            )
            push_ops.append(ExpressionNode(push))
        
        return BlockNode([
            init,
            *push_ops,
            array_var  # Return the array
        ])

    def visit_ArrayAccessNode(self, node):
        # Transform array access to function call
        array = self.visit(node.array)
        index = self.visit(node.index)
        return CallNode('__array_get__', [array, index])

    def visit_ArrayAssignNode(self, node):
        # Transform array assignment to function call
        array = self.visit(node.array)
        index = self.visit(node.index)
        value = self.visit(node.value)
        return CallNode('__array_set__', [array, index, value])

    def visit_FuncNode(self, node):
        # Transform function declarations to assignable values
        func_name = node.name
        params = node.params
        body = [self.visit(stmt) for stmt in node.body]
        
        # Create a lambda expression
        lambda_expr = LambdaNode(params, BlockNode(body))
        
        # Return an assignment
        return AssignmentNode(
            IdentifierNode(func_name),
            lambda_expr
        )