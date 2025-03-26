# amatak/runtime.py
import os
import sys
from typing import Dict, Optional

class AMatakRuntime:
    """Amatak Language Runtime"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.interpreter = AMatakInterpreter(self)
        self._globals: Dict = {
            'print': self._builtin_print,
            'f': self._format_string,
        }
        
    def execute(self, code: str, filename: str = '<string>') -> None:
        """Execute Amatak source code"""
        try:
            # Parse and execute the code
            parsed = self._parse(code)
            self._execute_ast(parsed)
        except Exception as e:
            raise RuntimeError(f"Error executing {filename}: {str(e)}")
            
    def execute_file(self, filename: str, debug: bool = False) -> None:
        """Execute an Amatak script file"""
        with open(filename, 'r', encoding='utf-8') as f:
            code = f.read()
        self.execute(code, filename)
        
    def compile(self, filename: str) -> str:
        """Compile Amatak source to bytecode"""
        # In a real implementation, this would generate bytecode
        base_name = os.path.splitext(filename)[0]
        output_file = f"{base_name}.amc"  # Amatak Compiled
        with open(output_file, 'wb') as f:
            f.write(b"AMATAK_BYTECODE")  # Placeholder
        return output_file
        
    def _parse(self, code: str):
        """Parse Amatak code (simplified)"""
        # In a real implementation, this would use a proper parser
        return {'type': 'program', 'body': code}
        
    def _execute_ast(self, ast):
        """Execute parsed AST (simplified)"""
        # This is a placeholder - real implementation would walk the AST
        # For now, we'll just use Python's exec with some transformations
        py_code = self._amatak_to_python(ast['body'])
        exec(py_code, self._globals)
        
    def _amatak_to_python(self, code: str) -> str:
        """Convert Amatak syntax to Python (temporary solution)"""
        # Note: This is just for the demo - a real implementation would use a proper parser
        
        # Convert func to def
        code = code.replace('func ', 'def ')
        
        # Convert f-strings (they're the same in Python)
        # Convert {x} to {x} (same in Python)
        
        # Convert loops
        code = code.replace('for ', 'for ')
        # (same syntax in this simple case)
        
        return code
        
    def _builtin_print(self, *args, **kwargs):
        """Built-in print function"""
        print(*args, **kwargs)
        
    def _format_string(self, s: str) -> str:
        """String formatting function"""
        return s  # Actual formatting would happen during execution

class AMatakInterpreter:
    """Interactive REPL interpreter"""
    
    def __init__(self, runtime):
        self.runtime = runtime
        self._locals = {}
        
    def start_repl(self):
        """Start interactive REPL"""
        print(f"Amatak REPL (Type 'exit' to quit)")
        while True:
            try:
                code = input('>>> ')
                if code.strip().lower() in ('exit', 'quit'):
                    break
                    
                # Execute the code
                self.runtime.execute(code, '<repl>')
                
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt")
            except Exception as e:
                print(f"Error: {e}")