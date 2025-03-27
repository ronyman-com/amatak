# test_functions.py - Python test runner
import unittest
from amatak.interpreter import Interpreter
from amatak.parser import Parser
from amatak.lexer import Lexer
import sys
from io import StringIO

class TestFunctionsAmatak(unittest.TestCase):
    def setUp(self):
        # Python comments use #
        self.interpreter = Interpreter([], debug=True)
        self.held_output = StringIO()
        sys.stdout = self.held_output
    
    def tearDown(self):
        sys.stdout = sys.__stdout__
    
    def run_amatak_code(self, code):
        lexer = Lexer(code, debug=True)
        parser = Parser(lexer.get_tokens(), debug=True)
        self.interpreter.tree = parser.parse()
        self.interpreter.interpret()
        return self.held_output.getvalue()

    def test_math_functions(self):
        code = """
        // Amatak code with // comments
        function abs(x) {
            if x < 0 { return -x }
            return x
        }
        print "abs(-5) = " + abs(-5)
        """
        output = self.run_amatak_code(code)
        print(f"\nTest Output:\n{output}")  # This will show in console
        self.assertIn("abs(-5) = 5", output)

if __name__ == "__main__":
    unittest.main(verbosity=2)