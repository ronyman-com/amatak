#!/usr/bin/env python3
import sys
import os
from amatak.runtime import AMatakRuntime

def print_help():
    print("""Amatak Language CLI
Usage:
  amatak run <file.ak>    # Execute Amatak file
  amatak build <file.ak>  # Compile to bytecode
  amatak serve [dir]      # Start dev server
  amatak repl             # Start interactive REPL
  amatak help             # Show this help
""")

def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    rt = AMatakRuntime()
    command = sys.argv[1]
    
    try:
        if command == 'run':
            if len(sys.argv) < 3:
                print("Error: Missing filename")
                print_help()
                sys.exit(1)
            rt.execute_file(sys.argv[2])
        elif command == 'build':
            if len(sys.argv) < 3:
                print("Error: Missing filename")
                print_help()
                sys.exit(1)
            rt.compile(sys.argv[2])
        elif command == 'serve':
            root = sys.argv[2] if len(sys.argv) > 2 else '.'
            from amatak.servers import start_dev_server
            start_dev_server(root)
        elif command == 'repl':
            rt.interpreter.start_repl()
        elif command == 'help':
            print_help()
        else:
            print(f"Error: Unknown command '{command}'")
            print_help()
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()