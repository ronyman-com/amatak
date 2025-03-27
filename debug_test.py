#!/usr/bin/env python3
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Now import Lexer and test
from amatak.lexer import Lexer

try:
    print("Testing Lexer initialization...")
    lexer = Lexer("test", debug=True)
    print(f"✅ Success! Debug flag: {lexer.debug}")
    print(f"Lexer module path: {Lexer.__module__}")
    print(f"Lexer class parameters: {Lexer.__init__.__code__.co_varnames}")
except Exception as e:
    print(f"❌ Failed: {e}")
    print("Python path:")
    for p in sys.path:
        print(f"  {p}")