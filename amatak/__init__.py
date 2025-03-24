"""Amatak: A modern, embeddable scripting language."""
from .lexer import Lexer, Token
from .parser import Parser
from .interpreter import Interpreter
from .errors import AmatakError, AmatakSyntaxError, AmatakRuntimeError
from .nodes import (
    ASTNode, FuncNode, CallNode, PrintNode, 
    StringNode, NumberNode, BinOpNode, IdentifierNode
)

__all__ = [
    'Lexer', 'Token', 'Parser', 'Interpreter',
    'AmatakError', 'AmatakSyntaxError', 'AmatakRuntimeError',
    'ASTNode', 'FuncNode', 'CallNode', 'PrintNode',
    'StringNode', 'NumberNode', 'BinOpNode', 'IdentifierNode'
]

__version__ = "0.1.0"