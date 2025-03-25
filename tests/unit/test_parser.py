import pytest
from amatak.parser import Parser
from amatak.lexer import Lexer
from amatak.nodes import *

class TestParser:
    def parse_expr(self, text):
        lexer = Lexer(text)
        parser = Parser(lexer)
        return parser.parse_expression()

    def parse_stmt(self, text):
        lexer = Lexer(text)
        parser = Parser(lexer)
        return parser.parse_statement()

    def test_literals(self):
        # Test number literal
        node = self.parse_expr("123")
        assert isinstance(node, NumberNode)
        assert node.value == 123

        # Test string literal
        node = self.parse_expr('"hello"')
        assert isinstance(node, StringNode)
        assert node.value == "hello"

    def test_binary_ops(self):
        # Test addition
        node = self.parse_expr("1 + 2")
        assert isinstance(node, BinOpNode)
        assert node.op == '+'
        assert isinstance(node.left, NumberNode)
        assert isinstance(node.right, NumberNode)

        # Test precedence
        node = self.parse_expr("1 + 2 * 3")
        assert isinstance(node, BinOpNode)
        assert node.op == '+'
        assert isinstance(node.right, BinOpNode)
        assert node.right.op == '*'

    def test_unary_ops(self):
        # Test negation
        node = self.parse_expr("-5")
        assert isinstance(node, UnaryOpNode)
        assert node.op == '-'
        assert isinstance(node.operand, NumberNode)

    def test_variables(self):
        # Test variable reference
        node = self.parse_expr("x")
        assert isinstance(node, VarNode)
        assert node.name == "x"

        # Test assignment
        node = self.parse_stmt("x = 5")
        assert isinstance(node, AssignNode)
        assert node.name == "x"
        assert isinstance(node.value, NumberNode)

    def test_if_statement(self):
        node = self.parse_stmt("if (x) { 1 } else { 2 }")
        assert isinstance(node, IfNode)
        assert isinstance(node.condition, VarNode)
        assert len(node.then_branch) == 1
        assert len(node.else_branch) == 1

    def test_while_loop(self):
        node = self.parse_stmt("while (x < 10) { x = x + 1 }")
        assert isinstance(node, WhileNode)
        assert isinstance(node.condition, BinOpNode)
        assert len(node.body) == 1

    def test_function(self):
        node = self.parse_stmt("func add(x, y) { return x + y }")
        assert isinstance(node, FunctionNode)
        assert node.params == ['x', 'y']
        assert len(node.body) == 1
        assert isinstance(node.body[0], ReturnNode)

    def test_error_handling(self):
        with pytest.raises(Exception):
            self.parse_expr("1 +")
        
        with pytest.raises(Exception):
            self.parse_stmt("if (x) {")