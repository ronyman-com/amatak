# scripts/benchmark.py
import timeit
from amatak.interpreter import Interpreter
from amatak.lexer import tokenize
from amatak.parser import Parser

def run_benchmark():
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
    execution_time = timeit.timeit(run_benchmark, number=10)
    print(f"Execution time: {execution_time} seconds")