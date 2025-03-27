from .errors import AmatakSyntaxError
from .tokens import Token, TokenType


class Lexer:
    def __init__(self, text: str, debug: bool = False):  # Added debug parameter here
        """Initialize the lexer with source text."""
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.current_char = self.text[self.pos] if self.text else None
        self.symbols = TokenType.get_symbols()
        self.keywords = TokenType.get_keywords()
        self.debug = debug  # Now properly using the parameter

    def error(self, message: str):
        """Raise a syntax error with current position."""
        if self.debug:
            print(f"Lexer Error [L{self.line}:C{self.column}]: {message}")
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
        """Skip whitespace characters including spaces, tabs, etc. except newlines."""
        while (self.current_char is not None and 
              self.current_char.isspace() and 
              self.current_char != '\n'):
            self.advance()

    def skip_comment(self):
        """Skip both single-line (//) and multi-line (/* */) comments."""
        if self.current_char == '/' and self.pos + 1 < len(self.text):
            next_char = self.text[self.pos + 1]
            # Single-line comment
            if next_char == '/':
                self.advance()  # Skip first /
                self.advance()  # Skip second /
                while self.current_char is not None and self.current_char != '\n':
                    self.advance()
                return True
            # Multi-line comment
            elif next_char == '*':
                self.advance()  # Skip /
                self.advance()  # Skip *
                while self.current_char is not None:
                    if (self.current_char == '*' and 
                        self.pos + 1 < len(self.text) and 
                        self.text[self.pos + 1] == '/'):
                        self.advance()  # Skip *
                        self.advance()  # Skip /
                        return True
                    self.advance()
                self.error("Unterminated multi-line comment")
        return False

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
        
        while (self.current_char is not None and 
              (self.current_char.isdigit() or self.current_char == '.')):
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
        
        # Read the entire word
        while (self.current_char is not None and 
              (self.current_char.isalnum() or 
               self.current_char == '_')):
            result += self.current_char
            self.advance()
        
        # Check if it's a keyword (case-sensitive)
        token_type = self.keywords.get(result, TokenType.IDENTIFIER)
        return Token(token_type, result, start_line, start_col)

    def get_tokens(self) -> list[Token]:
        """Convert the source text into a list of tokens."""
        tokens = []
        iterations = 0
        MAX_ITERATIONS = len(self.text) * 3  # Safety limit to prevent infinite loops
        
        while self.current_char is not None and iterations < MAX_ITERATIONS:
            iterations += 1
            
            # Skip whitespace (except newlines which we want to track)
            if self.current_char.isspace():
                if self.current_char == '\n':
                    tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
                    self.advance()
                else:
                    self.skip_whitespace()
                continue
                
            # Handle comments
            if self.skip_comment():
                continue
                
            # Handle string literals
            if self.current_char == '"':
                tokens.append(self.get_string())
                continue
                
            # Handle numbers
            if self.current_char.isdigit() or self.current_char == '.':
                tokens.append(self.get_number())
                continue
                
            # Handle identifiers/keywords
            if self.current_char.isalpha() or self.current_char == '_':
                tokens.append(self.get_identifier_or_keyword())
                continue
                
            # Handle symbols
            matched_symbol = None
            for symbol in sorted(self.symbols.keys(), key=len, reverse=True):
                if self.text.startswith(symbol, self.pos):
                    matched_symbol = symbol
                    break
                    
            if matched_symbol:
                token_type = self.symbols[matched_symbol]
                tokens.append(Token(token_type, matched_symbol, self.line, self.column))
                for _ in matched_symbol:
                    self.advance()
                continue
                
            # If we get here, it's an unrecognized character
            self.error(f"Unknown character: '{self.current_char}' at {self.line}:{self.column}")
        
        if iterations >= MAX_ITERATIONS:
            self.error(f"Lexer stuck after processing {iterations} characters")
        
        tokens.append(Token(TokenType.EOF, "", self.line, self.column))
        return tokens