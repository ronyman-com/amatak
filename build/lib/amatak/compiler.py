import os
import marshal
import zlib
from .env import AmatakEnvironment

class AmatakCompiler:
    def __init__(self, env=None):
        self.env = env or AmatakEnvironment()
        self.optimize = True

    def compile_source(self, source, output_path=None):
        """Compile Amatak source to bytecode"""
        from .parser import Parser
        from .lexer import Lexer
        
        lexer = Lexer(source)
        tokens = lexer.scan_tokens()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        if self.optimize:
            from .core.ast.optimizer import ASTOptimizer
            ast = ASTOptimizer().optimize(ast)
        
        bytecode = marshal.dumps(ast)
        compressed = zlib.compress(bytecode)
        
        if output_path:
            with open(output_path, 'wb') as f:
                f.write(b'AMTK' + len(compressed).to_bytes(4, 'big') + compressed)
        
        return compressed

    def compile_file(self, input_path, output_path=None):
        """Compile an Amatak source file"""
        with open(input_path, 'r') as f:
            source = f.read()
        
        if not output_path:
            base = os.path.splitext(input_path)[0]
            output_path = f'{base}.akc'
        
        return self.compile_source(source, output_path)