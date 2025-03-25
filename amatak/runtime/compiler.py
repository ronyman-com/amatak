import pickle
from ..parser import Parser
from ..lexer import Lexer

class Compiler:
    def __init__(self):
        self.optimize = True
        self.target = 'bytecode'  # or 'native'

    def compile(self, source):
        """Compile Amatak source to bytecode"""
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        if self.optimize:
            from ..core.ast.optimizer import ASTOptimizer
            optimizer = ASTOptimizer()
            ast = optimizer.optimize(ast)
        
        # Serialize AST to bytecode
        bytecode = pickle.dumps(ast)
        
        # Add header with version info
        header = b'AMATAK' + (1).to_bytes(2, 'big')  # Version 1
        return header + bytecode

    def compile_to_native(self, source):
        """Compile to native code (future feature)"""
        raise NotImplementedError("Native compilation not yet implemented")