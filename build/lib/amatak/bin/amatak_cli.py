#!/usr/bin/env python3
"""Amatak Language CLI Implementation"""

import sys
import os
import argparse
import traceback
from pathlib import Path
from typing import Optional, List, Dict, Any

# Ensure local package import precedence
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from amatak.lexer import Lexer
from amatak.parser import Parser
from amatak.interpreter import Interpreter, Context
from amatak.errors import AmatakError
from amatak.nodes import NodeVisitor

class AmatakCLI:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.runtime = self._init_runtime()
        self.setup_stdlib_functions()

    def _init_runtime(self):
        """Initialize the runtime components"""
        class Runtime:
            def __init__(self, debug):
                self.debug = debug
                self.interpreter = None
                self.context = Context()  # Initialize context here
                
            def execute(self, code, filename='<string>'):
                """Execute Amatak source code"""
                try:
                    lexer = Lexer(code, debug=self.debug)
                    tokens = lexer.get_tokens()
                    
                    parser = Parser(tokens, debug=self.debug)
                    tree = parser.parse()
                    
                    self.interpreter = Interpreter(tree, debug=self.debug, context=self.context)
                    return self.interpreter.interpret()
                except Exception as e:
                    raise AmatakError(f"Runtime error: {str(e)}")
                

            def compile(self, filename: str) -> str:
                """Compile Amatak source to bytecode"""
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    base_name = os.path.splitext(filename)[0]
                    output_file = f"{base_name}.amc"
                    
                    # In a real implementation, this would generate actual bytecode
                    with open(output_file, 'wb') as f:
                        f.write(b"AMATAK_BYTECODE")
                    
                    return output_file
                except Exception as e:
                    raise AmatakError(f"Compilation error: {str(e)}")

            def start_repl(self):
                """Start enhanced interactive REPL"""
                print("Amatak REPL (Type 'exit' or 'quit' to exit)")
                while True:
                    try:
                        code = input('>>> ')
                        if code.strip().lower() in ('exit', 'quit'):
                            break
                        if not code.strip():
                            continue
                            
                        try:
                            result = self.execute(code, '<repl>')
                            if result is not None:
                                print(result)
                        except AmatakError as e:
                            print(f"Error: {e}")
                    except KeyboardInterrupt:
                        print("\nKeyboardInterrupt")
                        break
                    except Exception as e:
                        print(f"Unexpected error: {e}")

        return Runtime(self.debug)

    def setup_stdlib_functions(self):
        """Register standard library functions in the runtime context"""
        # Core functions
        self.runtime.context.set('print', self._builtin_print)
        self.runtime.context.set('len', self._builtin_len)
        self.runtime.context.set('range', self._builtin_range)
        
        # Math functions
        self.runtime.context.set('abs', abs)
        self.runtime.context.set('pow', pow)
        self.runtime.context.set('round', round)
        
        # Type conversion
        self.runtime.context.set('int', int)
        self.runtime.context.set('float', float)
        self.runtime.context.set('str', str)

    def _builtin_print(self, *args):
        """Built-in print function"""
        print(' '.join(str(arg) for arg in args))

    def _builtin_len(self, obj):
        """Built-in len function"""
        if hasattr(obj, '__len__'):
            return len(obj)
        raise AmatakError(f"Object of type {type(obj)} has no len()")

    def _builtin_range(self, start, stop=None, step=1):
        """Built-in range function"""
        if stop is None:
            start, stop = 0, start
        return list(range(start, stop, step))

    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with subcommands"""
        parser = argparse.ArgumentParser(
            description='Amatak Language CLI',
            usage='amatak [command] [options]'
        )
        
        subparsers = parser.add_subparsers(dest='command', required=True)
        
        # Run command
        run_parser = subparsers.add_parser('run', help='Execute Amatak script')
        run_parser.add_argument('file', help='Amatak source file')
        run_parser.add_argument('--debug', action='store_true', help='Enable debug output')
        
        # Build command
        build_parser = subparsers.add_parser('build', help='Compile to bytecode')
        build_parser.add_argument('file', help='Amatak source file')
        build_parser.add_argument('--debug', action='store_true', help='Enable debug output')
        
        # REPL command
        repl_parser = subparsers.add_parser('repl', help='Start interactive REPL')
        repl_parser.add_argument('--debug', action='store_true', help='Enable debug output')
        
        # Version command
        parser.add_argument('--version', action='store_true', help='Show version information')
        
        return parser

    def print_version(self):
        """Print version information"""
        from amatak import __version__
        print(f"Amatak Language {__version__}")

    def handle_run(self, filename: str):
        """Handle the run command"""
        if not os.path.exists(filename):
            raise AmatakError(f"File not found: {filename}")
        
        abs_path = os.path.abspath(filename)
        
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            if self.debug:
                print(f"Executing: {abs_path}")
                
            result = self.runtime.execute(code, filename=abs_path)
            if result is not None and self.debug:
                print(f"Return value: {result}")
            
        except Exception as e:
            raise AmatakError(f"Error executing {filename}: {str(e)}")

    def handle_build(self, filename: str):
        """Handle the build command"""
        if not os.path.exists(filename):
            raise AmatakError(f"File not found: {filename}")
        
        output_file = self.runtime.compile(filename)
        print(f"Compiled to: {output_file}")

    def main(self):
        """Main CLI entry point"""
        parser = self.create_parser()
        args = parser.parse_args()
        
        self.debug = args.debug if hasattr(args, 'debug') else False

        if args.version:
            self.print_version()
            return

        try:
            if args.command == 'run':
                self.handle_run(args.file)
            elif args.command == 'build':
                self.handle_build(args.file)
            elif args.command == 'repl':
                self.runtime.start_repl()
        except AmatakError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)

def main():
    """Entry point for console script"""
    cli = AmatakCLI()
    cli.main()

if __name__ == '__main__':
    main()