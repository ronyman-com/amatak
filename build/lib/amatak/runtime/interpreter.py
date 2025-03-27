import sys
import os
from ..parser import Parser
from ..lexer import Lexer
from ..errors import AmatakRuntimeError
from .scope import Scope

class Interpreter:
    def __init__(self):
        self.scope = Scope()
        self.modules = {}
        self.debug = False

    def add_module(self, name, module):
        """Register a module for import"""
        self.modules[name] = module

    def execute(self, source):
        """Execute Amatak source code"""
        try:
            lexer = Lexer(source)
            tokens = lexer.scan_tokens()
            
            parser = Parser(tokens)
            ast = parser.parse()
            
            if self.debug:
                self._print_ast(ast)
            
            self._execute_ast(ast)
        except AmatakRuntimeError as e:
            print(f"Runtime error: {e}")
            sys.exit(1)

    def execute_bytecode(self, bytecode):
        """Execute compiled bytecode"""
        # TODO: Implement bytecode execution
        raise NotImplementedError("Bytecode execution not yet implemented")

    def _execute_ast(self, nodes):
        """Execute AST nodes"""
        for node in nodes:
            result = node.evaluate(self.scope)
            
            # Handle return statements
            if hasattr(result, 'should_return'):
                return result.value
            
            # Print expression results in REPL mode
            if self.repl_mode and result is not None:
                print(result)

    def _print_ast(self, nodes, indent=0):
        """Debug utility to print AST"""
        for node in nodes:
            print('  ' * indent + str(node))
            if hasattr(node, 'body'):
                self._print_ast(node.body, indent + 1)

    def start_repl(self):
        """Start interactive REPL"""
        print("Amatak REPL (type 'exit' to quit)")
        self.repl_mode = True
        
        while True:
            try:
                source = input(">>> ")
                if source.strip().lower() in ('exit', 'quit'):
                    break
                
                if not source:
                    continue
                
                self.execute(source)
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}")