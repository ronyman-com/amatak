#!/usr/bin/env python3
import sys
from amatak.lexer import Lexer
from amatak.parser import Parser
from amatak.interpreter import Interpreter
from amatak.errors import AmatakError

def run_file(filename):
    try:
        with open(filename, 'r') as file:
            text = file.read()
        
        lexer = Lexer(text)
        tokens = lexer.get_tokens()

        # In amatak.py, after getting tokens: remove this after check
        #rint("Generated tokens:")
        #or token in tokens:
            #rint(f"  {token}")
        ####################################


        
        parser = Parser(tokens)
        tree = parser.parse()

        # In amatak.py, after parsing: remove this after check
       #print("Generated AST:")
        #or node in tree:
            #pint(f"  {node}")
        #############################

        interpreter = Interpreter(tree)
        interpreter.interpret()
        
    except AmatakError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: amatak <file>")
        sys.exit(1)
    run_file(sys.argv[1])