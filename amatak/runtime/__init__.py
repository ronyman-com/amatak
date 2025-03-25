from .interpreter import Interpreter
from .compiler import Compiler
from .memory import MemoryManager
from .types import TypeSystem
from ..error_handling import error_handler
from ..security.middleware import security_middleware
from ..debug import debug_tools

class AMatakRuntime:
    def __init__(self, debug: bool = False):
        self.interpreter = Interpreter()
        self.compiler = Compiler()
        self.memory = MemoryManager()
        self.types = TypeSystem()
        
        # Initialize standard library
        self._init_stdlib()
         # Configure error handling
        error_handler.debug = debug
        
        # Configure security
        self.security = security_middleware
        
        # Configure debugging
        debug_tools.enabled = debug
        self.debug = debug_tools
        
        # Initialize other components with error handling
        self.interpreter = error_handler.wrap_operation(Interpreter)
        self.compiler = error_handler.wrap_operation(Compiler)
        
    @security_middleware.secure_operation
    def execute(self, source: str):
        """Secure execution with error handling"""
        return error_handler.wrap_operation(
            self.interpreter.execute,
            source
        )
        
    @debug_tools.trace
    def compile(self, source: str):
        """Traced compilation with error handling"""
        return error_handler.wrap_operation(
            self.compiler.compile,
            source
        )
        

    def _init_stdlib(self):
        """Initialize standard library functions"""
        from ..stdlib import math, strings, arrays
        self.interpreter.add_module('math', math)
        self.interpreter.add_module('strings', strings)
        self.interpreter.add_module('arrays', arrays)

    def execute_file(self, filename):
        """Execute an Amatak source file"""
        try:
            with open(filename, 'r') as f:
                source = f.read()
            self.interpreter.execute(source)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Runtime error: {str(e)}")
            sys.exit(1)

    def compile(self, filename):
        """Compile an Amatak source file to bytecode"""
        try:
            with open(filename, 'r') as f:
                source = f.read()
            
            # Get base filename without extension
            base_name = os.path.splitext(os.path.basename(filename))[0]
            output_file = f"{base_name}.akc"
            
            bytecode = self.compiler.compile(source)
            with open(output_file, 'wb') as f:
                f.write(bytecode)
            
            print(f"Compiled {filename} to {output_file}")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Compilation error: {str(e)}")
            sys.exit(1)

    def execute_bytecode(self, filename):
        """Execute compiled Amatak bytecode"""
        try:
            with open(filename, 'rb') as f:
                bytecode = f.read()
            self.interpreter.execute_bytecode(bytecode)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found")
            sys.exit(1)
        except Exception as e:
            print(f"Bytecode execution error: {str(e)}")
            sys.exit(1)


    def execute(self, source, scope=None):
        """Execute source code with a custom scope"""
        if scope is None:
            scope = {}
        
        # Create a new scope with the provided variables
        self.interpreter.scope = Scope()
        for name, value in scope.items():
            self.interpreter.scope.declare(name, value)
        
        return self.interpreter.execute(source)
    
       