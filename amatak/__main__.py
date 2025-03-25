import sys
from .bootstrap import AmatakBootstrap

def main():
    if len(sys.argv) < 2:
        print("Usage: amatak [run|compile] <file.amatak>")
        sys.exit(1)
    
    bootstrap = AmatakBootstrap()
    
    try:
        if sys.argv[1] == 'run':
            bootstrap.run_file(sys.argv[2])
        elif sys.argv[1] == 'compile':
            from .compiler import AmatakCompiler
            compiler = AmatakCompiler()
            compiler.compile_file(sys.argv[2])
        else:
            print(f"Unknown command: {sys.argv[1]}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()