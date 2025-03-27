from amatak.nodes import (
    FuncNode, CallNode, PrintNode,
    StringNode, IdentifierNode, BinOpNode,
    NumberNode, ArrayNode, ArrayAccessNode,
    ForNode, AssignmentNode
)
from amatak.errors import AmatakSyntaxError
from amatak.tokens import TokenType


class Parser:
    def __init__(self, tokens, debug=False):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None
        self.debug = debug

    def error(self, message):
        if self.debug:
            print(f"PARSER ERROR: {message}")
        if self.current_token:
            raise AmatakSyntaxError(
                message=message,
                line=self.current_token.line,
                column=self.current_token.column
            )
        raise AmatakSyntaxError(message)

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def expect(self, token_type, err_msg):
        if not self.current_token or self.current_token.type != token_type:
            self.error(err_msg)
        value = self.current_token.value
        self.advance()
        return value

    def skip_newlines(self):
        while self.current_token and self.current_token.type == TokenType.NEWLINE:
            self.advance()

    def parse(self):
        statements = []
        self.skip_newlines()
        
        while self.current_token and self.current_token.type != TokenType.EOF:
            if self.current_token.type == TokenType.NEWLINE:
                self.advance()
                continue
                
            if self.current_token.type == TokenType.FUNC:
                statements.append(self.parse_function())
            elif self.current_token.type == TokenType.PRINT:
                statements.append(self.parse_print())
            elif self.current_token.type == TokenType.LET:
                statements.append(self.parse_assignment())
            elif self.current_token.type == TokenType.FOR:
                statements.append(self.parse_for_loop())
            elif self.current_token.type == TokenType.IDENTIFIER:
                if (self.pos + 2 < len(self.tokens)):
                    # Check for method calls (numbers.push(6))
                    if (self.tokens[self.pos + 1].type == TokenType.DOT and
                        self.tokens[self.pos + 2].type == TokenType.IDENTIFIER and
                        self.tokens[self.pos + 3].type == TokenType.LPAREN):
                        statements.append(self.parse_method_call())
                    # Check for array assignments (numbers[0] = 10)
                    elif (self.tokens[self.pos + 1].type == TokenType.LBRACKET and
                        self.tokens[self.pos + 3].type == TokenType.RBRACKET and
                        self.tokens[self.pos + 4].type == TokenType.ASSIGN):
                        statements.append(self.parse_array_assignment())
                    # Check for regular assignments (x = 5)
                    elif self.tokens[self.pos + 1].type == TokenType.ASSIGN:
                        statements.append(self.parse_assignment())
                    # Check for function calls (func())
                    elif self.current_token.type == TokenType.IDENTIFIER:
                        # Handle method calls first
                        if (self.pos + 2 < len(self.tokens) and
                            self.tokens[self.pos + 1].type == TokenType.DOT and
                            self.tokens[self.pos + 2].type == TokenType.IDENTIFIER and
                            self.tokens[self.pos + 3].type == TokenType.LPAREN):
                            statements.append(self.parse_method_call())
                else:
                    statements.append(self.parse_expression())
            else:
                self.error(f"Unexpected token: {self.current_token.type}")
                
            self.skip_newlines()
            
        return statements

    def parse_method_call(self):
        """Parse method calls like numbers.push(6)"""
        obj = IdentifierNode(self.expect(TokenType.IDENTIFIER, "Expected object name"))
        self.expect(TokenType.DOT, "Expected '.' for method call")
        method = IdentifierNode(self.expect(TokenType.IDENTIFIER, "Expected method name"))
        self.expect(TokenType.LPAREN, "Expected '(' for method call")
        
        args = []
        if self.current_token.type != TokenType.RPAREN:
            # Handle numeric arguments
            if self.current_token.type == TokenType.NUMBER:
                args.append(NumberNode(self.current_token.value))
                self.advance()
            else:
                args.append(self.parse_expression())
            
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                if self.current_token.type == TokenType.NUMBER:
                    args.append(NumberNode(self.current_token.value))
                    self.advance()
                else:
                    args.append(self.parse_expression())
        
        self.expect(TokenType.RPAREN, "Expected ')' after arguments")
        return MethodCallNode(obj, method, args)

    def parse_array_assignment(self):
        """Parse array assignments like numbers[0] = 10"""
        array = IdentifierNode(self.expect(TokenType.IDENTIFIER, "Expected array name"))
        self.expect(TokenType.LBRACKET, "Expected '[' for array access")
        index = self.parse_expression()
        self.expect(TokenType.RBRACKET, "Expected ']' for array access")
        self.expect(TokenType.ASSIGN, "Expected '=' in array assignment")
        value = self.parse_expression()
        return AssignmentNode(ArrayAccessNode(array, index), value)

    def parse_array_access(self, array):
        """Parse array access: array[expr] or array[expr] = value"""
        self.expect(TokenType.LBRACKET, "Expected '[' for array access")
        index = self.parse_expression()
        self.expect(TokenType.RBRACKET, "Expected ']' for array access")
        
        # Check if this is an array assignment
        if self.current_token and self.current_token.type == TokenType.ASSIGN:
            self.advance()  # Skip '='
            value = self.parse_expression()
            return AssignmentNode(ArrayAccessNode(array, index), value)
        
        return ArrayAccessNode(array, index)

    def parse_print(self):
        self.expect(TokenType.PRINT, "Expected 'print' keyword")
        
        if self.current_token and self.current_token.type == TokenType.LPAREN:
            self.advance()
            value = self.parse_expression()
            self.expect(TokenType.RPAREN, "Expected ')' after expression")
        else:
            value = self.parse_expression()
            
        return PrintNode(value)

    def parse_assignment(self):
        if self.current_token.type == TokenType.LET:
            self.advance()
        
        target = self.parse_lvalue()
        self.expect(TokenType.ASSIGN, "Expected '=' in assignment")
        value = self.parse_expression()
        return AssignmentNode(target, value)

    def parse_lvalue(self):
        if self.current_token.type != TokenType.IDENTIFIER:
            self.error("Expected variable name")
        
        name = self.current_token.value
        self.advance()
        
        if self.current_token and self.current_token.type == TokenType.LBRACKET:
            return self.parse_array_access(IdentifierNode(name))
        
        return IdentifierNode(name)


    

    def parse_expression(self):
        """Parse expressions with binary operators."""
        node = self.parse_primary()
        
        # Handle array access
        while self.current_token and self.current_token.type == TokenType.LBRACKET:
            self.advance()
            index = self.parse_expression()
            self.expect(TokenType.RBRACKET, "Expected ']' after array index")
            node = ArrayAccessNode(node, index)
        
        # Handle binary operations
        while self.current_token and self.current_token.type in (
            TokenType.PLUS, TokenType.MINUS, TokenType.MUL, TokenType.DIV,
            TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE,
            TokenType.EQ, TokenType.NEQ
        ):
            op = self.current_token.type
            self.advance()
            node = BinOpNode(node, op, self.parse_primary())
        
        return node

    def parse_primary(self):
        """Parse primary expressions."""
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
            # Check if function call
            if (self.pos + 1 < len(self.tokens)) and self.tokens[self.pos + 1].type == TokenType.LPAREN:
                return self.parse_call()
            value = self.current_token.value
            self.advance()
            return IdentifierNode(value)
            
        elif self.current_token.type == TokenType.LPAREN:
            self.advance()
            node = self.parse_expression()
            self.expect(TokenType.RPAREN, "Expected ')' after expression")
            return node
            
        elif self.current_token.type == TokenType.LBRACKET:
            return self.parse_array()
            
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
            if self.current_token.type == TokenType.NEWLINE:
                self.advance()
                continue
            body.append(self.parse())
            
        self.expect(TokenType.RBRACE, "Expected '}'")
        return ForNode(var_name, start, condition, step, body)
    