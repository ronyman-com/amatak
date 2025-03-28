#!/usr/bin/env python3
"""
Amatak REPL - Read-Eval-Print Loop Interface
"""

import sys
import os
from pathlib import Path
from amatak import __version__
from amatak.interpreter import Interpreter
from amatak.lexer import Lexer
from amatak.parser import Parser
from amatak.errors import AmatakError

# Readline setup for better REPL experience
try:
    import readline  # Unix systems
except ImportError:
    try:
        import pyreadline as readline  # Windows fallback
        # Fix for Python 3.10+ compatibility
        import collections
        if not hasattr(collections, 'Callable'):
            collections.Callable = collections.abc.Callable
    except ImportError:
        readline = None  # No readline support

class AmatakREPL:
    def __init__(self, debug=False):
        self.debug = debug
        self.context = {}
        self._setup_history()
        
    def _setup_history(self):
        """Initialize readline history if available"""
        if not readline:
            return
            
        histfile = os.path.join(os.path.expanduser("~"), ".amatak_history")
        try:
            readline.read_history_file(histfile)
        except FileNotFoundError:
            pass
            
        readline.set_history_length(1000)
        
        # Register history save on exit
        import atexit
        atexit.register(self._save_history, histfile)
        
    def _save_history(self, histfile):
        """Save command history"""
        if readline:
            try:
                readline.write_history_file(histfile)
            except Exception:
                pass

    def _get_input_prompt(self, continuation=False):
        """Get the appropriate input prompt"""
        return "... " if continuation else ">>> "

    def _print_banner(self):
        """Display REPL welcome banner"""
        print(f"Amatak REPL {__version__}")
        print("Type 'exit', 'quit' or Ctrl-D to exit\n")

    def _print_result(self, result):
        """Format and print evaluation results"""
        if result is not None:
            print(f"=> {result}")

    def run(self):
        """Main REPL execution loop"""
        self._print_banner()
        
        buffer = ""
        while True:
            try:
                # Get input with appropriate prompt
                prompt = self._get_input_prompt(continuation=bool(buffer))
                try:
                    line = input(prompt)
                except EOFError:
                    print()  # Newline after Ctrl-D
                    break
                
                # Skip empty lines
                if not line.strip() and not buffer:
                    continue
                    
                # Add to buffer or execute
                buffer += line + "\n"
                
                try:
                    # Try parsing to check for complete statements
                    lexer = Lexer(buffer, debug=self.debug)
                    parser = Parser(lexer.get_tokens(), debug=self.debug)
                    parser.parse()
                    
                    # If parsing succeeds, execute
                    result = Interpreter(parser.tree, context=self.context).interpret()
                    self._print_result(result)
                    buffer = ""
                except AmatakError as e:
                    # If parsing fails, continue input unless we're at start of line
                    if not buffer.strip():
                        print(f"Error: {e}")
                        buffer = ""
                        
            except KeyboardInterrupt:
                print("\nKeyboardInterrupt")
                buffer = ""
            except Exception as e:
                print(f"Unexpected error: {e}")
                buffer = ""

def main():
    """Entry point for standalone REPL"""
    try:
        repl = AmatakREPL(debug='--debug' in sys.argv)
        repl.run()
    except Exception as e:
        print(f"Failed to start REPL: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()