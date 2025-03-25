#!/usr/bin/env python3
"""Amatak Language Command Line Interface"""

import sys
from typing import Optional
from amatak.runtime import AMatakRuntime
from amatak.errors import AmatakError

def print_help() -> None:
    """Display CLI usage information"""
    print("""Amatak Language CLI

Usage:
  amatak run <file.amatak>    Execute Amatak script
  amatak build <file.amatak>  Compile to bytecode
  amatak serve [directory]    Start development server
  amatak repl                 Start interactive REPL
  amatak help                 Show this help message

Options:
  --debug    Enable debug output
  --version  Show version information
""")

def print_version() -> None:
    """Display version information"""
    from amatak import __version__
    print(f"Amatak Language {__version__}")

def handle_run(runtime: AMatakRuntime, filename: str, debug: bool = False) -> None:
    """Execute an Amatak script file"""
    if not os.path.exists(filename):
        raise AmatakError(f"File not found: {filename}")
    runtime.execute_file(filename, debug=debug)

def handle_build(runtime: AMatakRuntime, filename: str) -> None:
    """Compile an Amatak script to bytecode"""
    if not os.path.exists(filename):
        raise AmatakError(f"File not found: {filename}")
    output_file = runtime.compile(filename)
    print(f"Compiled to: {output_file}")

def handle_serve(directory: Optional[str] = None) -> None:
    """Start development server"""
    from amatak.servers import start_dev_server
    start_dev_server(directory or '.')

def parse_args() -> tuple:
    """Parse command line arguments"""
    debug = '--debug' in sys.argv
    version = '--version' in sys.argv
    
    # Filter out options
    args = [arg for arg in sys.argv[1:] if not arg.startswith('--')]
    
    return args, debug, version

def main() -> None:
    """Main CLI entry point"""
    args, debug, version = parse_args()

    if version:
        print_version()
        return

    if not args or args[0] == 'help':
        print_help()
        return

    command = args[0]
    runtime = AMatakRuntime(debug=debug)

    try:
        if command == 'run':
            if len(args) < 2:
                raise AmatakError("Missing filename for 'run' command")
            handle_run(runtime, args[1], debug)
        elif command == 'build':
            if len(args) < 2:
                raise AmatakError("Missing filename for 'build' command")
            handle_build(runtime, args[1])
        elif command == 'serve':
            handle_serve(args[1] if len(args) > 1 else None)
        elif command == 'repl':
            runtime.interpreter.start_repl()
        else:
            raise AmatakError(f"Unknown command: '{command}'")
    except AmatakError as e:
        print(f"Error: {e}", file=sys.stderr)
        print_help()
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()