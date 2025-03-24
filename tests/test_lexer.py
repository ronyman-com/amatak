import unittest
from amatak.lexer import Lexer
from amatak.tokens import Token, TokenType

class TestLexer(unittest.TestCase):
    def test_lexer(self):
        lexer = Lexer('print("Hello")')
        tokens = []
        while (token := lexer.next_token()).type != TokenType.EOF:
            tokens.append(token)
        self.assertEqual(tokens, [
            Token(TokenType.IDENTIFIER, "print"),
            Token(TokenType.LPAREN, "("),
            Token(TokenType.STRING, "Hello"),
            Token(TokenType.RPAREN, ")"),
        ])