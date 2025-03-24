# tests/test_interpreter.py
import unittest
from amatak.lexer import Lexer
from amatak.parser import Parser
from amatak.interpreter import Interpreter

class TestInterpreter(unittest.TestCase):
    def test_interpret(self):
        code = 'let x = 10'
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = Interpreter()
        interpreter.interpret(ast)
        self.assertEqual(interpreter.variables["x"], 10)

if __name__ == "__main__":
    unittest.main()