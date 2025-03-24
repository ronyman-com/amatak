from amatak.nodes import (
    FuncNode, CallNode, PrintNode,
    StringNode, IdentifierNode, BinOpNode,
    NumberNode
)
from amatak.errors import AmatakSyntaxError
from amatak.tokens import TokenType

class Parser:
    def __init__(self, tokens):
        """Initialize parser with token stream."""
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None

    def error(self, message):
        """Raise syntax error with current position."""
        if self.current_token:
            raise AmatakSyntaxError(
                message=message,
                line=self.current_token.line,
                column=self.current_token.column
            )
        raise AmatakSyntaxError(message)

    def advance(self):
        """Move to next token in stream."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = None

    def expect(self, token_type, err_msg):
        """Verify current token matches expected type."""
        if not self.current_token or self.current_token.type != token_type:
            self.error(err_msg)
        value = self.current_token.value
        self.advance()
        return value

    def parse(self):
        """Parse complete token stream into AST."""
        statements = []
        while self.current_token and self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.FUNC:
                statements.append(self.parse_function())
            elif self.current_token.type == TokenType.PRINT:
                statements.append(self.parse_print())
            elif self.current_token.type == TokenType.IDENTIFIER:
                statements.append(self.parse_call())
            else:
                self.error(f"Unexpected token: {self.current_token.type}")
        return statements

    def parse_function(self):
        """Parse function definition: func name(params) { body }"""
        self.expect(TokenType.FUNC, "Expected 'func' keyword")
        
        func_name = self.expect(
            TokenType.IDENTIFIER,
            "Expected function name after 'func'"
        )
        
        self.expect(TokenType.LPAREN, "Expected '(' after function name")
        
        params = []
        if self.current_token and self.current_token.type != TokenType.RPAREN:
            params.append(self.expect(
                TokenType.IDENTIFIER,
                "Expected parameter name"
            ))
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()  # Skip comma
                params.append(self.expect(
                    TokenType.IDENTIFIER,
                    "Expected parameter name after comma"
                ))
        
        self.expect(TokenType.RPAREN, "Expected ')' after parameters")
        self.expect(TokenType.LBRACE, "Expected '{' before function body")
        
        body = []
        while self.current_token and self.current_token.type != TokenType.RBRACE:
            if self.current_token.type == TokenType.PRINT:
                body.append(self.parse_print())
            else:
                self.error("Only print statements allowed in function body for now")
        
        self.expect(TokenType.RBRACE, "Expected '}' after function body")
        return FuncNode(func_name, params, body)

    def parse_call(self):
        """Parse function call: name(args)"""
        func_name = self.expect(
            TokenType.IDENTIFIER,
            "Expected function name"
        )
        
        self.expect(TokenType.LPAREN, "Expected '(' after function name")
        
        args = []
        if self.current_token and self.current_token.type != TokenType.RPAREN:
            args.append(self.parse_expression())
            while self.current_token and self.current_token.type == TokenType.COMMA:
                self.advance()  # Skip comma
                args.append(self.parse_expression())
        
        self.expect(TokenType.RPAREN, "Expected ')' after arguments")
        return CallNode(func_name, args)

    def parse_print(self):
        """Parse print statement: print(expr)"""
        self.expect(TokenType.PRINT, "Expected 'print' keyword")
        self.expect(TokenType.LPAREN, "Expected '(' after 'print'")
        
        value = self.parse_expression()
        
        self.expect(TokenType.RPAREN, "Expected ')' after expression")
        return PrintNode(value)

    def parse_expression(self):
        """Parse expressions with binary operators."""
        if self.current_token.type == TokenType.LBRACKET:
             return self.parse_array()
        node = self.parse_primary()
        
        while self.current_token and self.current_token.type in (
            TokenType.PLUS, 
            TokenType.MINUS,
            TokenType.MUL,
            TokenType.DIV
        ):
            op = self.current_token.type
            self.advance()
            node = BinOpNode(node, op, self.parse_primary())
        
        return node

    def parse_primary(self):
        """Parse primary expressions (literals, identifiers, grouped expressions)."""
        if not self.current_token:
            self.error("Unexpected end of input")
        
        if self.current_token.type == TokenType.STRING:
            value = self.current_token.value
            self.advance()
            return StringNode(value)
            
        elif self.current_token.type == TokenType.NUMBER:
            value = self.current_token.value
            self.advance()
            return NumberNode(value)
            
        elif self.current_token.type == TokenType.IDENTIFIER:
            value = self.current_token.value
            self.advance()
            return IdentifierNode(value)
            
        elif self.current_token.type == TokenType.LPAREN:
            self.advance()
            node = self.parse_expression()
            self.expect(TokenType.RPAREN, "Expected ')' after expression")
            return node
            
        self.error(f"Unexpected token: {self.current_token.type}")




    def parse_array(self):
        """Parse array literal: [expr, expr, ...]"""
        self.expect(TokenType.LBRACKET, "Expected '['")
        elements = []
        if self.current_token.type != TokenType.RBRACKET:
            elements.append(self.parse_expression())
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                elements.append(self.parse_expression())
        self.expect(TokenType.RBRACKET, "Expected ']'")
        return ArrayNode(elements)

    def parse_array_access(self, array):
        """Parse array access: array[expr]"""
        self.expect(TokenType.LBRACKET, "Expected '[' for array access")
        index = self.parse_expression()
        self.expect(TokenType.RBRACKET, "Expected ']' for array access")
        return ArrayAccessNode(array, index)

    def parse_for_loop(self):
        """Parse for loop: for let i = 0; i < len; i = i + 1 { ... }"""
        self.expect(TokenType.FOR, "Expected 'for'")
        self.expect(TokenType.LET, "Expected 'let' in for loop")
        var_name = self.expect(TokenType.IDENTIFIER, "Expected variable name")
        self.expect(TokenType.ASSIGN, "Expected '=' in for loop")
        start = self.parse_expression()
        self.expect(TokenType.SEMI, "Expected ';'")
        condition = self.parse_expression()
        self.expect(TokenType.SEMI, "Expected ';'")
        step = self.parse_expression()
        self.expect(TokenType.LBRACE, "Expected '{'")
        body = []
        while self.current_token.type != TokenType.RBRACE:
            body.append(self.parse_statement())
        self.expect(TokenType.RBRACE, "Expected '}'")
        return ForNode(var_name, start, condition, step, body)