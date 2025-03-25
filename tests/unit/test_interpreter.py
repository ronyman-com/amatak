import pytest
from amatak.interpreter import Interpreter
from amatak.nodes import *

class TestInterpreter:
    @pytest.fixture
    def interpreter(self):
        return Interpreter([])

    def test_number_literal(self, interpreter):
        node = NumberNode(42)
        assert interpreter.visit(node) == 42

    def test_string_literal(self, interpreter):
        node = StringNode("hello")
        assert interpreter.visit(node) == "hello"

    def test_binary_operations(self, interpreter):
        # Test addition
        add_node = BinOpNode(NumberNode(2), '+', NumberNode(3))
        assert interpreter.visit(add_node) == 5

        # Test string concatenation
        concat_node = BinOpNode(StringNode("a"), '+', StringNode("b"))
        assert interpreter.visit(concat_node) == "ab"

    def test_unary_operations(self, interpreter):
        # Test negation
        neg_node = UnaryOpNode('-', NumberNode(5))
        assert interpreter.visit(neg_node) == -5

        # Test logical not
        not_node = UnaryOpNode('!', BooleanNode(True))
        assert interpreter.visit(not_node) is False

    def test_variable_assignment(self, interpreter):
        # Test variable assignment and lookup
        assign_node = AssignNode('x', NumberNode(10))
        var_node = VarNode('x')
        
        interpreter.visit(assign_node)
        assert interpreter.visit(var_node) == 10

    def test_if_statement(self, interpreter):
        # Test if with true condition
        if_node = IfNode(
            BooleanNode(True),
            [NumberNode(1)],
            [NumberNode(2)]
        )
        assert interpreter.visit(if_node) == 1

        # Test if with false condition
        if_node.condition = BooleanNode(False)
        assert interpreter.visit(if_node) == 2

    def test_while_loop(self, interpreter):
        # Test while loop
        interpreter.variables['counter'] = 0
        while_node = WhileNode(
            BinOpNode(VarNode('counter'), '<', NumberNode(3)),
            [
                AssignNode('counter', 
                    BinOpNode(VarNode('counter'), '+', NumberNode(1)))
            ]
        )
        
        interpreter.visit(while_node)
        assert interpreter.variables['counter'] == 3

    def test_function_call(self, interpreter):
        # Test function call
        interpreter.functions['square'] = FunctionNode(
            ['x'],
            [ReturnNode(BinOpNode(VarNode('x'), '*', VarNode('x')))]
        )
        
        call_node = CallNode('square', [NumberNode(4)])
        assert interpreter.visit(call_node) == 16

    def test_error_handling(self, interpreter):
        # Test invalid operation
        invalid_node = BinOpNode(NumberNode(1), '&', NumberNode(2))
        with pytest.raises(RuntimeError):
            interpreter.visit(invalid_node)