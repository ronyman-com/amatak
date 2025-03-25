import os
import sys
import marshal
from .env import AmatakEnvironment

class AmatakBootstrap:
    def __init__(self):
        self.env = AmatakEnvironment()
        self._load_core()

    def _load_core(self):
        """Load core Amatak components"""
        # Load bytecode-compiled core modules
        core_modules = [
            'lexer', 'parser', 'compiler', 
            'interpreter', 'runtime', 'types'
        ]
        
        for mod in core_modules:
            try:
                bytecode_path = self.env.stdlib_path / f'{mod}.akc'
                with open(bytecode_path, 'rb') as f:
                    code = marshal.load(f)
                module = type(sys)(mod)
                exec(code, module.__dict__)
                sys.modules[f'amatak.{mod}'] = module
            except Exception as e:
                raise ImportError(f"Failed to load core module {mod}: {str(e)}")

    def execute(self, source, args=None):
        """Execute Amatak source code"""
        from .interpreter import Interpreter
        interpreter = Interpreter(self.env)
        return interpreter.execute(source, args or [])

    def run_file(self, file_path):
        """Run an Amatak script file"""
        with open(file_path, 'r') as f:
            source = f.read()
        return self.execute(source, sys.argv[1:])