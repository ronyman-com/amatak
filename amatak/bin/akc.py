#!/usr/bin/env python3
import sys
import argparse
from amatak.compiler import Compiler

def main():
    parser = argparse.ArgumentParser(description="Amatak Compiler")
    parser.add_argument("input", help="Input .amatak file")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument("--optimize", action="store_true", help="Enable optimizations")
    parser.add_argument("--target", choices=["bytecode", "native"], default="bytecode")
    
    args = parser.parse_args()
    
    compiler = Compiler()
    compiler.optimize = args.optimize
    compiler.target = args.target
    
    with open(args.input, "r") as f:
        source = f.read()
    
    output = args.output or f"{os.path.splitext(args.input)[0]}.akc"
    
    try:
        bytecode = compiler.compile(source)
        with open(output, "wb") as f:
            f.write(bytecode)
        print(f"Successfully compiled {args.input} to {output}")
    except Exception as e:
        print(f"Compilation failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()