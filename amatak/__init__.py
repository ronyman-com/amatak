"""Amatak: A modern, embeddable scripting language."""

import sys
import warnings
import atexit
from typing import List, Any

# Core components
from .lexer import Lexer, Token
from .parser import Parser
from .interpreter import Interpreter
from .errors import AmatakError, AmatakSyntaxError, AmatakRuntimeError
from .nodes import (
    ASTNode, FuncNode, CallNode, PrintNode,
    StringNode, NumberNode, BinOpNode, IdentifierNode
)

# Set Python context marker
sys._amatak_python_context = True

# Initialize loader system
try:
    from .loader import load_module, clear_cache, install_loader, uninstall_loader
    loader_available = True
    install_loader(priority=1)
    atexit.register(uninstall_loader)
except ImportError as e:
    loader_available = False
    warnings.warn(f"Loader system unavailable: {str(e)}")

# Package metadata
__version__ = "0.1.0"
__author__ = "Rony MAN"
__email__ = "amatak.io@outlook.com"
__license__ = "MIT"

def run(code: str, debug: bool = False) -> Any:
    """
    Execute Amatak code directly.
    
    Args:
        code: Amatak source code to execute
        debug: Enable debug output
        
    Returns:
        Result of the execution
    """
    try:
        lexer = Lexer(code, debug=debug)
        parser = Parser(lexer.get_tokens(), debug=debug)
        interpreter = Interpreter(parser.parse(), debug=debug)
        return interpreter.interpret()
    except AmatakError as e:
        warnings.warn(f"Execution error: {str(e)}")
        raise

def parse(code: str, debug: bool = False) -> ASTNode:
    """
    Parse Amatak code into AST.
    
    Args:
        code: Amatak source code to parse
        debug: Enable debug output
        
    Returns:
        Root AST node
    """
    try:
        lexer = Lexer(code, debug=debug)
        parser = Parser(lexer.get_tokens(), debug=debug)
        return parser.parse()
    except AmatakError as e:
        warnings.warn(f"Parse error: {str(e)}")
        raise

def tokenize(code: str, debug: bool = False) -> List[Token]:
    """
    Tokenize Amatak code.
    
    Args:
        code: Amatak source code to tokenize
        debug: Enable debug output
        
    Returns:
        List of tokens
    """
    try:
        lexer = Lexer(code, debug=debug)
        return lexer.get_tokens()
    except AmatakError as e:
        warnings.warn(f"Tokenization error: {str(e)}")
        raise

__all__ = [
    # Core components
    'Lexer', 'Token', 'Parser', 'Interpreter',
    
    # Error types
    'AmatakError', 'AmatakSyntaxError', 'AmatakRuntimeError',
    
    # AST Nodes
    'ASTNode', 'FuncNode', 'CallNode', 'PrintNode',
    'StringNode', 'NumberNode', 'BinOpNode', 'IdentifierNode',
    
    # Loader system
    'load_module', 'clear_cache', 'install_loader', 'uninstall_loader',
    
    # Utility functions
    'run', 'parse', 'tokenize'
]