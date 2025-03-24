from .errors import AmatakSyntaxError
from .tokens import Token, TokenType

class Lexer:
    def __init__(self, text: str):
        """Initialize the lexer with source text."""
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[self.pos] if self.text else None
        self.symbols = TokenType.get_symbols()
        self.keywords = TokenType.get_keywords()

    def error(self, message: str):
        """Raise a syntax error with current position."""
        raise AmatakSyntaxError(message, self.line, self.column)

    def advance(self):
        """Move to the next character in the source text."""
        if self.current_char == '\n':
            self.line += 1
            self.column = 0
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
            self.column += 1
        else:
            self.current_char = None

    def skip_whitespace(self):
        """Skip whitespace characters except newlines."""
        while self.current_char is not None and self.current_char.isspace() and self.current_char != '\n':
            self.advance()

    def skip_comment(self):
        """Skip single-line comments."""
        if self.current_char == '#':
            while self.current_char is not None and self.current_char != '\n':
                self.advance()
            if self.current_char == '\n':
                self.advance()

    def get_string(self) -> Token:
        """Read a string literal and return a STRING token."""
        result = ""
        start_line = self.line
        start_col = self.column
        self.advance()  # Skip opening quote
        
        while self.current_char is not None and self.current_char != '"':
            if self.current_char == '\\':
                self.advance()  # Skip escape character
                if self.current_char is None:
                    self.error("Unterminated string literal")
                result += self.current_char
            else:
                result += self.current_char
            self.advance()
            
        if self.current_char != '"':
            self.error("Unterminated string literal")
            
        self.advance()  # Skip closing quote
        return Token(TokenType.STRING, result, start_line, start_col)

    def get_number(self) -> Token:
        """Read a number literal and return a NUMBER token."""
        result = ""
        start_line = self.line
        start_col = self.column
        decimal_points = 0
        
        while self.current_char is not None and (self.current_char.isdigit() or self.current_char == '.'):
            if self.current_char == '.':
                decimal_points += 1
                if decimal_points > 1:
                    self.error("Invalid number with multiple decimal points")
            result += self.current_char
            self.advance()
            
        if result.startswith('.'):
            result = '0' + result
        if result.endswith('.'):
            result += '0'
            
        return Token(TokenType.NUMBER, result, start_line, start_col)

    def get_identifier_or_keyword(self) -> Token:
        """Read an identifier or keyword and return the appropriate token."""
        result = ""
        start_line = self.line
        start_col = self.column
        
        while self.current_char is not None and (self.current_char.isalnum() or self.current_char == '_'):
            result += self.current_char
            self.advance()
            
        # Check if it's a keyword
        token_type = self.keywords.get(result, TokenType.IDENTIFIER)
        return Token(token_type, result, start_line, start_col)

    def get_tokens(self) -> list[Token]:
        """Convert the source text into a list of tokens."""
        tokens = []
        
        while self.current_char is not None:
            # Skip whitespace first
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
                
            # Handle comments
            if self.current_char == '#':
                self.skip_comment()
                continue
                
            # Handle strings
            if self.current_char == '"':
                tokens.append(self.get_string())
                continue
                
            # Handle numbers
            if self.current_char.isdigit():
                tokens.append(self.get_number())
                continue
                
            # Handle identifiers and keywords
            if self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.get_identifier_or_keyword())
                continue
                
            # Handle symbols
            if self.current_char in self.symbols:
                # Check for multi-character operators first
                if self.current_char in ('=', '!', '<', '>'):
                    peek_pos = self.pos + 1
                    if peek_pos < len(self.text):
                        combined = self.current_char + self.text[peek_pos]
                        if combined in self.symbols:
                            token_type = self.symbols[combined]
                            tokens.append(Token(token_type, combined, self.line, self.column))
                            self.advance()  # Skip first char
                            self.advance()  # Skip second char
                            continue
                
                # Single-character symbol
                token_type = self.symbols[self.current_char]
                tokens.append(Token(token_type, self.current_char, self.line, self.column))
                self.advance()
                continue
                
            # If we get here, it's an unrecognized character
            self.error(f"Unknown character: '{self.current_char}'")
        
        # Add EOF token at the end
        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens