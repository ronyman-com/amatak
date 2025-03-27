#!/usr/bin/env python3
import sys
from amatak.lexer import Lexer

try:
    lexer = Lexer("test", debug=True)
    print("✅ Lexer accepts debug parameter correctly")
    print(f"Lexer source: {Lexer.__module__}")
    print(f"Debug flag value: {lexer.debug}")
except Exception as e:
    print(f"❌ Lexer error: {e}")
    print(f"Current parameters: {Lexer.__init__.__code__.co_varnames}")
    print("Python path:")
    for p in sys.path:
        print(f"  {p}")