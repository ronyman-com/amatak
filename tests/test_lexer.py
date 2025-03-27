from amatak.lexer import Lexer

# Test basic lexer initialization
try:
    lexer = Lexer("test", debug=True)
    print("✅ Lexer initialized successfully with debug=True")
    lexer = Lexer("test")
    print("✅ Lexer initialized successfully with debug=False")
except Exception as e:
    print(f"❌ Lexer initialization failed: {e}")