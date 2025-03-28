#!/usr/bin/env python3
"""Enhanced Amatak Language CLI with Database Terminal"""

import sys
import os
import argparse
import traceback
from pathlib import Path
from typing import Optional, List, Dict, Any
from tabulate import tabulate

# Fix for Python 3.10+ compatibility before importing readline
import collections.abc
if sys.version_info >= (3, 10) and not hasattr(collections, 'Callable'):
    collections.Callable = collections.abc.Callable

# Ensure local package import precedence
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from amatak import __version__
from amatak.interpreter import Interpreter, Context
from amatak.lexer import Lexer
from amatak.parser import Parser
from amatak.errors import AmatakError

# Database support check
try:
    from amatak.database.drivers import SQLiteDriver, PostgresDriver
    from amatak.database import connect
    DB_SUPPORT = True
except ImportError as e:
    print(f"Warning: Database support disabled - {str(e)}", file=sys.stderr)
    DB_SUPPORT = False

class DatabaseTerminal:
    """Interactive database terminal with Windows support"""
    
    def __init__(self, driver):
        self.driver = driver
        self.prompt = "db> "
        self.history_file = os.path.expanduser("~/.amatak_db_history")
        
    def start(self):
        """Start the interactive database terminal"""
        driver_name = self.driver.__class__.__name__.replace("Driver", "")
        print(f"\nAmatak Database Terminal ({driver_name})")
        print("Type SQL commands or 'exit'/'quit' to exit\n")
        
        try:
            while True:
                try:
                    query = input(self.prompt).strip()
                    if not query:
                        continue
                    if query.lower() in ('exit', 'quit'):
                        break
                        
                    self._execute_and_display(query)
                except KeyboardInterrupt:
                    print("\n(To exit, type 'exit' or 'quit')")
                except Exception as e:
                    print(f"Error: {e}")
        finally:
            self._save_history()

    def _execute_and_display(self, query):
        """Execute query and display results"""
        try:
            results = self.driver.execute(query)
            if results:
                if isinstance(results[0], dict):  # PostgreSQL
                    headers = list(results[0].keys())
                    rows = [list(row.values()) for row in results]
                else:  # SQLite
                    headers = [f"Column {i+1}" for i in range(len(results[0]))]
                    rows = results
                
                print(tabulate(rows, headers=headers))
                print(f"\n({len(results)} row{'s' if len(results) != 1 else ''} returned)")
            else:
                print("Query executed successfully (no results)")
        except Exception as e:
            raise AmatakError(f"Database error: {str(e)}")

    def _save_history(self):
        """Save command history if available"""
        pass

class AmatakCLI:
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.runtime = self._init_runtime()
        self.setup_stdlib_functions()
        if DB_SUPPORT:
            self.setup_database_commands()

    def _init_runtime(self):
        """Initialize the runtime components"""
        class Runtime:
            def __init__(self, debug):
                self.debug = debug
                self.interpreter = None
                self.context = Context()
                self.db_connections = {}
                
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
                    
                    with open(output_file, 'wb') as f:
                        f.write(b"AMATAK_BYTECODE")
                    
                    return output_file
                except Exception as e:
                    raise AmatakError(f"Compilation error: {str(e)}")

            def start_repl(self):
                """Start enhanced interactive REPL"""
                print(f"Amatak REPL {__version__} (Type 'exit' or 'quit' to exit)")
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

    def setup_database_commands(self):
        """Register database commands in the runtime context"""
        self.runtime.context.set('db_connect', self.runtime.db_connect)
        self.runtime.context.set('db_execute', self.runtime.db_execute)
        self.runtime.context.set('db_disconnect', self.runtime.db_disconnect)

    def setup_stdlib_functions(self):
        """Register standard library functions in the runtime context"""
        self.runtime.context.set('print', self._builtin_print)
        self.runtime.context.set('len', self._builtin_len)
        self.runtime.context.set('range', self._builtin_range)
        self.runtime.context.set('abs', abs)
        self.runtime.context.set('pow', pow)
        self.runtime.context.set('round', round)
        self.runtime.context.set('int', int)
        self.runtime.context.set('float', float)
        self.runtime.context.set('str', str)

    def _builtin_print(self, *args):
        print(' '.join(str(arg) for arg in args))

    def _builtin_len(self, obj):
        if hasattr(obj, '__len__'):
            return len(obj)
        raise AmatakError(f"Object of type {type(obj)} has no len()")

    def _builtin_range(self, start, stop=None, step=1):
        if stop is None:
            start, stop = 0, start
        return list(range(start, stop, step))

    def create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with subcommands"""
        parser = argparse.ArgumentParser(
            description=f'Amatak Language CLI v{__version__}',
            usage='amatak [command] [options]'
        )
        
        subparsers = parser.add_subparsers(dest='command', required=True)
        
        run_parser = subparsers.add_parser('run', help='Execute Amatak script')
        run_parser.add_argument('file', help='Amatak source file')
        run_parser.add_argument('--debug', action='store_true')
        
        build_parser = subparsers.add_parser('build', help='Compile to bytecode')
        build_parser.add_argument('file', help='Amatak source file')
        build_parser.add_argument('--debug', action='store_true')
        
        repl_parser = subparsers.add_parser('repl', help='Start interactive REPL')
        repl_parser.add_argument('--debug', action='store_true')
        
        if DB_SUPPORT:
            db_parser = subparsers.add_parser('db', help='Start database terminal')
            db_parser.add_argument('--type', choices=['sqlite', 'postgres'], required=True)
            db_parser.add_argument('--path', help='SQLite database path')
            db_parser.add_argument('--host', help='PostgreSQL host', default='localhost')
            db_parser.add_argument('--port', type=int, default=5432)
            db_parser.add_argument('--dbname', help='PostgreSQL database name')
            db_parser.add_argument('--user', help='PostgreSQL username')
            db_parser.add_argument('--password', help='PostgreSQL password')
        
        parser.add_argument('--version', action='store_true', help='Show version')
        return parser

    def handle_db_terminal(self, args):
        try:
            if args.type == 'sqlite':
                db_path = args.path or ':memory:'
                print(f"Connecting to SQLite database at: {db_path}")
                driver = SQLiteDriver()
                driver.connect(db_path)
            elif args.type == 'postgres':
                print(f"Connecting to PostgreSQL at: {args.host}:{args.port}")
                driver = PostgresDriver()
                driver.connect({
                    'host': args.host,
                    'port': args.port,
                    'dbname': args.dbname,
                    'user': args.user,
                    'password': args.password
                })
            
            terminal = DatabaseTerminal(driver)
            terminal.start()
        except Exception as e:
            print(f"Failed to start database terminal: {e}", file=sys.stderr)
            sys.exit(1)

    def print_version(self):
        print(f"Amatak Language v{__version__}")
        print("Copyright (c) 2025 Amatak Project")

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
            if result is not None and self.debug:
                print(f"Return value: {result}")
        except Exception as e:
            raise AmatakError(f"Error executing {filename}: {str(e)}")

    def handle_build(self, filename: str):
        if not os.path.exists(filename):
            raise AmatakError(f"File not found: {filename}")
        
        output_file = self.runtime.compile(filename)
        print(f"Compiled to: {output_file}")

    def main(self):
        """Main CLI entry point"""
        parser = self.create_parser()
        args = parser.parse_args()
        
        self.debug = getattr(args, 'debug', False)

        if getattr(args, 'version', False):
            self.print_version()
            return
            
        try:
            if args.command == 'run':
                self.handle_run(args.file)
            elif args.command == 'build':
                self.handle_build(args.file)
            elif args.command == 'repl':
                self.runtime.start_repl()
            elif args.command == 'db' and DB_SUPPORT:
                self.handle_db_terminal(args)
        except AmatakError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}", file=sys.stderr)
            sys.exit(1)

def main():
    """Main CLI entry point"""
    cli = AmatakCLI()
    cli.main()

if __name__ == "__main__":
    main()