from enum import Enum
from typing import Dict, Optional, Any, List

class TokenType(Enum):
    """Enumeration of all token types in the Amatak language."""
    # Structural tokens
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    COMMA = ","
    DOT = "."
    SEMI = ";"
    COLON = ":"
    QUESTION = "?"
    MOD = "%" 

    # Operators
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    ASSIGN = "="
    EQ = "=="
    NEQ = "!="
    LT = "<"
    GT = ">"
    LTE = "<="
    GTE = ">="

    # Keywords
    LET = "let"
    FUNC = "func"
    PRINT = "print"
    RETURN = "return"
    IF = "if"
    ELSE = "else"
    TRUE = "true"
    FALSE = "false"
    AND = "and"
    OR = "or"
    NOT = "not"
    FOR = "for"
    IN = "in"
    PUSH = "push"
    POP = "pop"
    LEN = "len"

    # Literals
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"

    # Special tokens
    EOF = "EOF"
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"

    @classmethod
    def get_keywords(cls) -> Dict[str, 'TokenType']:
        """Returns a dictionary of keyword strings to their TokenTypes."""
        return {
            "let": cls.LET,
            "func": cls.FUNC,
            "print": cls.PRINT,
            "return": cls.RETURN,
            "if": cls.IF,
            "else": cls.ELSE,
            "true": cls.TRUE,
            "false": cls.FALSE,
            "and": cls.AND,
            "or": cls.OR,
            "not": cls.NOT,
            "for": cls.FOR,
            "in": cls.IN,
            "push": cls.PUSH,
            "pop": cls.POP,
            "len": cls.LEN
        }

    @classmethod
    def get_symbols(cls) -> Dict[str, 'TokenType']:
        """Returns a dictionary of symbol strings to their TokenTypes."""
        return {
            "(": cls.LPAREN,
            ")": cls.RPAREN,
            "{": cls.LBRACE,
            "}": cls.RBRACE,
            "[": cls.LBRACKET,
            "]": cls.RBRACKET,
            ",": cls.COMMA,
            ".": cls.DOT,
            ";": cls.SEMI,
            ":": cls.COLON,
            "+": cls.PLUS,
            "-": cls.MINUS,
            "*": cls.MUL,
            "/": cls.DIV,
            "=": cls.ASSIGN,
            "==": cls.EQ,
            "!=": cls.NEQ,
            "<": cls.LT,
            ">": cls.GT,
            "<=": cls.LTE,
            ">=": cls.GTE,
            "%": cls.MOD,
            "?":cls.QUESTION, 
        }


class Token:
    """Represents a token in the Amatak language."""
    
    def __init__(
        self,
        type_: TokenType,
        value: str,
        line: Optional[int] = None,
        column: Optional[int] = None
    ):
        """
        Args:
            type_: The type of the token (TokenType enum)
            value: The literal value of the token as it appeared in the source
            line: The line number where the token appears (1-based)
            column: The column number where the token appears (1-based)
        """
        self.type = type_
        self.value = value
        self.line = line
        self.column = column
    
    def __repr__(self) -> str:
        """Returns a detailed string representation of the token."""
        return (f"Token(type={self.type.name}, "
                f"value={self.value!r}, "
                f"line={self.line}, "
                f"column={self.column})")
    
    def __eq__(self, other: Any) -> bool:
        """Compares tokens for equality."""
        if not isinstance(other, Token):
            return False
        return (self.type == other.type and
                self.value == other.value and
                self.line == other.line and
                self.column == other.column)

    def is_type(self, *token_types: TokenType) -> bool:
        """Checks if token matches any of the given types."""
        return self.type in token_types