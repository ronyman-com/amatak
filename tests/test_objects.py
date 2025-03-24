import pytest
from amatak.lexer import tokenize
from amatak.parser import Parser
from amatak.interpreter import Interpreter

def test_object_creation():
    code = 'let obj = { "name": "Alice", "age": 25 }'
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)
    assert interpreter.variables['obj'] == {"name": "Alice", "age": 25}

def test_object_access():
    code = '''
    let obj = { "name": "Alice", "age": 25 }
    let name = obj["name"]
    '''
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)
    assert interpreter.variables['name'] == "Alice"

def test_object_assignment():
    code = '''
    let obj = { "name": "Alice", "age": 25 }
    obj["age"] = 26
    '''
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    interpreter.interpret(ast)
    assert interpreter.variables['obj'] == {"name": "Alice", "age": 26}

def test_object_invalid_key():
    code = '''
    let obj = { "name": "Alice", "age": 25 }
    let x = obj["invalid"]
    '''
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    with pytest.raises(KeyError):
        interpreter.interpret(ast)