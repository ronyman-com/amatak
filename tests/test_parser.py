import unittest
from amatak.parser import Parser
from amatak.lexer import Lexer
from amatak.tokens import Token, TokenType
from amatak.nodes import PrintNode, StringNode, FuncNode, CallNode, BinOpNode
from amatak.errors import AmatakSyntaxError

class TestParser(unittest.TestCase):
    def setUp(self):
        """Common setup for all tests"""
        self.maxDiff = None

    def test_parse_print_statement(self):
        """Test parsing a simple print statement"""
        lexer = Lexer('print("Hello")')
        tokens = lexer.get_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Should return a list of statements (single statement in this case)
        self.assertEqual(len(ast), 1)
        self.assertIsInstance(ast[0], PrintNode)
        self.assertIsInstance(ast[0].value, StringNode)
        self.assertEqual(ast[0].value.value, "Hello")

    def test_parse_function_definition(self):
        """Test parsing a function definition"""
        lexer = Lexer('func greet() { print("Hello") }')
        tokens = lexer.get_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertEqual(len(ast), 1)
        self.assertIsInstance(ast[0], FuncNode)
        self.assertEqual(ast[0].name, "greet")
        self.assertEqual(len(ast[0].params), 0)
        self.assertEqual(len(ast[0].body), 1)
        self.assertIsInstance(ast[0].body[0], PrintNode)

    def test_parse_function_call(self):
        """Test parsing a function call"""
        lexer = Lexer('greet("Alice")')
        tokens = lexer.get_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertEqual(len(ast), 1)
        self.assertIsInstance(ast[0], CallNode)
        self.assertEqual(ast[0].name, "greet")
        self.assertEqual(len(ast[0].args), 1)
        self.assertIsInstance(ast[0].args[0], StringNode)
        self.assertEqual(ast[0].args[0].value, "Alice")

    def test_parse_string_concatenation(self):
        """Test parsing string concatenation"""
        lexer = Lexer('print("Hello" + " World")')
        tokens = lexer.get_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        
        self.assertEqual(len(ast), 1)
        self.assertIsInstance(ast[0], PrintNode)
        self.assertIsInstance(ast[0].value, BinOpNode)
        self.assertEqual(ast[0].value.op, "+")
        self.assertIsInstance(ast[0].value.left, StringNode)
        self.assertIsInstance(ast[0].value.right, StringNode)

    def test_invalid_syntax_raises_error(self):
        """Test that invalid syntax raises AmatakSyntaxError"""
        test_cases = [
            ('print("Hello"', "Missing closing parenthesis"),
            ('func greet { print("Hi") }', "Missing parentheses in function definition"),
            ('greet("Alice"', "Missing closing parenthesis in function call"),
        ]
        
        for code, description in test_cases:
            with self.subTest(code=code, description=description):
                lexer = Lexer(code)
                tokens = lexer.get_tokens()
                parser = Parser(tokens)
                with self.assertRaises(AmatakSyntaxError):
                    parser.parse()

    def test_empty_input(self):
        """Test parsing empty input"""
        lexer = Lexer('')
        tokens = lexer.get_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        self.assertEqual(ast, [])

if __name__ == '__main__':
    unittest.main()