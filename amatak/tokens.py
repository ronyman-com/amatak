from enum import Enum
from typing import Optional, Dict, Any

class TokenType(Enum):
    """Enumeration of all token types in the Amatak language."""
    # Single-character tokens
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    COMMA = ","
    DOT = "."
    SEMI = ";"
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    ASSIGN = "="
    COLON = ":"
    
    # Comparison operators
    EQ = "=="
    NEQ = "!="
    LT = "<"
    GT = ">"
    LTE = "<="
    GTE = ">="
    
    # Literals
    IDENTIFIER = "IDENTIFIER"
    STRING = "STRING"
    NUMBER = "NUMBER"
    
    # Keywords
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
    
    # Special
    EOF = "EOF"
    NEWLINE = "NEWLINE"
    INDENT = "INDENT"
    DEDENT = "DEDENT"

    @classmethod
    def get_keywords(cls) -> Dict[str, 'TokenType']:
        """Returns a dictionary of keyword strings to their TokenTypes."""
        return {
            cls.FUNC.value: cls.FUNC,
            cls.PRINT.value: cls.PRINT,
            cls.RETURN.value: cls.RETURN,
            cls.IF.value: cls.IF,
            cls.ELSE.value: cls.ELSE,
            cls.TRUE.value: cls.TRUE,
            cls.FALSE.value: cls.FALSE,
            cls.AND.value: cls.AND,
            cls.OR.value: cls.OR,
            cls.NOT.value: cls.NOT,
        }

    @classmethod
    def get_symbols(cls) -> Dict[str, 'TokenType']:
        """Returns a dictionary of symbol strings to their TokenTypes."""
        return {
            cls.LPAREN.value: cls.LPAREN,
            cls.RPAREN.value: cls.RPAREN,
            cls.LBRACE.value: cls.LBRACE,
            cls.RBRACE.value: cls.RBRACE,
            cls.COMMA.value: cls.COMMA,
            cls.DOT.value: cls.DOT,
            cls.SEMI.value: cls.SEMI,
            cls.PLUS.value: cls.PLUS,
            cls.MINUS.value: cls.MINUS,
            cls.MUL.value: cls.MUL,
            cls.DIV.value: cls.DIV,
            cls.ASSIGN.value: cls.ASSIGN,
            cls.COLON.value: cls.COLON,
            cls.EQ.value: cls.EQ,
            cls.NEQ.value: cls.NEQ,
            cls.LT.value: cls.LT,
            cls.GT.value: cls.GT,
            cls.LTE.value: cls.LTE,
            cls.GTE.value: cls.GTE,
        }


class Token:
    """Represents a token in the Amatak language."""
    
    def __init__(self, type_: TokenType, value: str, line: Optional[int] = None, column: Optional[int] = None):
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
        """Compares tokens for equality.
        
        Args:
            other: Another object to compare with
            
        Returns:
            True if the tokens are equal, False otherwise
        """
        if not isinstance(other, Token):
            return False
        return (self.type == other.type and 
                self.value == other.value and
                self.line == other.line and
                self.column == other.column)

    def is_type(self, *token_types: TokenType) -> bool:
        """Checks if token matches any of the given types.
        
        Args:
            *token_types: One or more TokenType values to check against
            
        Returns:
            True if the token's type matches any of the given types
        """
        return self.type in token_types
    

        