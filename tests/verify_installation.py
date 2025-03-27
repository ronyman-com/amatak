import sys
from importlib import reload
import amatak.lexer

# Force reload the module
reload(amatak.lexer)

# Verify the Lexer class
try:
    lexer = amatak.lexer.Lexer("test", debug=True)
    print("✅ Lexer accepts debug parameter correctly")
    print(f"Lexer debug flag: {lexer.debug}")
except Exception as e:
    print(f"❌ Lexer still has issues: {e}")
    print("Current Lexer parameters:", 
          amatak.lexer.Lexer.__init__.__code__.co_varnames)