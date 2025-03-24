// test_arrays.py
from amatak.lexer import Lexer
from amatak.parser import Parser
from amatak.interpreter import Interpreter  // Assuming you have an interpreter

def test_arrays_example():
    with open("examples/arrays.amatak", "r") as f:
        code = f.read()
    
    // Lexing
    lexer = Lexer(code)
    tokens = lexer.get_tokens()
    print("Lexing completed successfully!")
    
    // Parsing
    parser = Parser(tokens)
    ast = parser.parse()
    print("Parsing completed successfully!")
    print("Generated AST:")
    for node in ast:
        print(node)
    
    // Interpretation (if you have an interpreter)
    interpreter = Interpreter()
    interpreter.interpret(ast)
    print("Interpretation completed!")

if __name__ == "__main__":
    test_arrays_example()