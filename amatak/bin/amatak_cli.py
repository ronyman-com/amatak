#!/usr/bin/env python3
"""Amatak Language CLI Implementation"""

import sys
import os
import argparse
from pathlib import Path
from typing import Optional

# Ensure local package import precedence
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from amatak.lexer import Lexer
from amatak.parser import Parser
from amatak.interpreter import Interpreter
from amatak.errors import AmatakError

class AmatakCLI:
    def __init__(self, debug=False):
        self.debug = debug
        self.runtime = self._init_runtime()
        
    def _init_runtime(self):
        """Initialize the runtime components"""
        class Runtime:
            def __init__(self, debug):
                self.debug = debug
                self.interpreter = None
                
            def execute(self, code, filename='<string>'):
                """Execute Amatak source code"""
                try:
                    if self.debug:
                        print(f"\n=== SOURCE CODE ===\n{code}\n")
                    
                    lexer = Lexer(code, debug=self.debug)
                    tokens = lexer.get_tokens()
                    
                    if self.debug:
                        print("\n=== TOKEN STREAM ===")
                        for i, token in enumerate(tokens):
                            print(f"{i:2d}: {token}")
                    
                    parser = Parser(tokens, debug=self.debug)
                    tree = parser.parse()
                    
                    if self.debug:
                        print("\n=== ABSTRACT SYNTAX TREE ===")
                        for i, node in enumerate(tree):
                            print(f"{i:2d}: {node}")
                    
                    self.interpreter = Interpreter(tree, debug=self.debug)
                    return self.interpreter.interpret()
                except Exception as e:
                    raise AmatakError(f"Runtime error: {str(e)}")
                
            def compile(self, filename):
                """Compile Amatak source to bytecode"""
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    base_name = os.path.splitext(filename)[0]
                    output_file = f"{base_name}.amc"
                    with open(output_file, 'wb') as f:
                        f.write(b"AMATAK_BYTECODE")
                    return output_file
                except Exception as e:
                    raise AmatakError(f"Compilation error: {str(e)}")
                
            def start_repl(self):
                """Start interactive REPL"""
                print("Amatak REPL (Type 'exit' or 'quit' to exit)")
                while True:
                    try:
                        code = input('>>> ')
                        if code.strip().lower() in ('exit', 'quit'):
                            break
                        if code.strip() == '':
                            continue
                        result = self.execute(code, '<repl>')
                        if result is not None:
                            print(result)
                    except KeyboardInterrupt:
                        print("\nKeyboardInterrupt")
                        break
                    except Exception as e:
                        print(f"Error: {e}")

        return Runtime(self.debug)

    def create_parser(self):
        """Create argument parser"""
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
        
        # Version flag
        parser.add_argument('--version', action='store_true', help='Show version information')
        
        return parser

    def print_version(self):
        from amatak import __version__
        print(f"Amatak Language {__version__}")

    def handle_run(self, filename: str):
        if not os.path.exists(filename):
            raise AmatakError(f"File not found: {filename}")
        
        abs_path = os.path.abspath(filename)
        
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                code = f.read()
            
            if self.debug:
                print(f"Executing: {abs_path}")
                
            result = self.runtime.execute(code, filename=abs_path)
            if result is not None:
                print(result)
            
        except Exception as e:
            raise AmatakError(f"Error executing {filename}: {str(e)}")

    def handle_build(self, filename: str):
        if not os.path.exists(filename):
            raise AmatakError(f"File not found: {filename}")
        
        output_file = self.runtime.compile(filename)
        print(f"Compiled to: {output_file}")

    def main(self):
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