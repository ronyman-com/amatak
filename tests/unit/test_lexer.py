import pytest
from amatak.lexer import Lexer
from amatak.tokens import TokenType

class TestLexer:
    def test_basic_tokens(self):
        lexer = Lexer("123 + 45.67 - \"hello\"")
        tokens = lexer.get_tokens()
        
        assert tokens[0].type == TokenType.NUMBER
        assert tokens[0].value == "123"
        
        assert tokens[1].type == TokenType.PLUS
        
        assert tokens[2].type == TokenType.NUMBER
        assert tokens[2].value == "45.67"
        
        assert tokens[3].type == TokenType.MINUS
        
        assert tokens[4].type == TokenType.STRING
        assert tokens[4].value == "hello"

    def test_keywords(self):
        lexer = Lexer("if else while func return true false")
        tokens = lexer.get_tokens()
        
        assert tokens[0].type == TokenType.IF
        assert tokens[1].type == TokenType.ELSE
        assert tokens[2].type == TokenType.WHILE
        assert tokens[3].type == TokenType.FUNC
        assert tokens[4].type == TokenType.RETURN
        assert tokens[5].type == TokenType.TRUE
        assert tokens[6].type == TokenType.FALSE

    def test_identifiers(self):
        lexer = Lexer("x _var1 myVar99")
        tokens = lexer.get_tokens()
        
        assert tokens[0].type == TokenType.IDENTIFIER
        assert tokens[0].value == "x"
        
        assert tokens[1].type == TokenType.IDENTIFIER
        assert tokens[1].value == "_var1"
        
        assert tokens[2].type == TokenType.IDENTIFIER
        assert tokens[2].value == "myVar99"

    def test_comments(self):
        lexer = Lexer("""
            // This is a comment
            123 /* Multi-line 
            comment */ 456
        """)
        tokens = lexer.get_tokens()
        
        assert len(tokens) == 3  # Only the numbers and EOF
        assert tokens[0].value == "123"
        assert tokens[1].value == "456"

    def test_error_handling(self):
        lexer = Lexer("123 @ 456")
        with pytest.raises(Exception):
            lexer.get_tokens()