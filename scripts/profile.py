# scripts/profile.py
import cProfile
from amatak.interpreter import Interpreter
from amatak.lexer import tokenize
from amatak.parser import Parser

def run_profiling():
    code = '''
    let x = 0
    while x < 10000 {
        x = x + 1
    }
    '''
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)

if __name__ == '__main__':
    cProfile.run('run_profiling()', sort='cumulative')