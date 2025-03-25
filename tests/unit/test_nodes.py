import pytest
from amatak.nodes import *

class TestNodes:
    def test_number_node(self):
        node = NumberNode(42)
        assert node.value == 42
        assert str(node) == "NumberNode(42)"

    def test_string_node(self):
        node = StringNode("hello")
        assert node.value == "hello"
        assert str(node) == "StringNode('hello')"

    def test_binary_op_node(self):
        left = NumberNode(1)
        right = NumberNode(2)
        node = BinOpNode(left, '+', right)
        
        assert node.left == left
        assert node.op == '+'
        assert node.right == right
        assert str(node) == "BinOpNode(NumberNode(1) + NumberNode(2))"

    def test_unary_op_node(self):
        operand = NumberNode(5)
        node = UnaryOpNode('-', operand)
        
        assert node.op == '-'
        assert node.operand == operand
        assert str(node) == "UnaryOpNode(-NumberNode(5))"

    def test_var_node(self):
        node = VarNode('x')
        assert node.name == 'x'
        assert str(node) == "VarNode(x)"

    def test_assign_node(self):
        node = AssignNode('x', NumberNode(10))
        assert node.name == 'x'
        assert isinstance(node.value, NumberNode)
        assert str(node) == "AssignNode(x = NumberNode(10))"

    def test_if_node(self):
        condition = BooleanNode(True)
        then_branch = [NumberNode(1)]
        else_branch = [NumberNode(2)]
        
        node = IfNode(condition, then_branch, else_branch)
        assert node.condition == condition
        assert node.then_branch == then_branch
        assert node.else_branch == else_branch
        assert str(node) == "IfNode(condition=BooleanNode(True))"

    def test_function_node(self):
        params = ['x', 'y']
        body = [ReturnNode(BinOpNode(VarNode('x'), '+', VarNode('y')))]
        
        node = FunctionNode(params, body)
        assert node.params == params
        assert node.body == body
        assert str(node) == "FunctionNode(params=['x', 'y'])"

    def test_call_node(self):
        args = [NumberNode(1), NumberNode(2)]
        node = CallNode('add', args)
        
        assert node.name == 'add'
        assert len(node.args) == 2
        assert str(node) == "CallNode(add, args=[NumberNode(1), NumberNode(2)])"