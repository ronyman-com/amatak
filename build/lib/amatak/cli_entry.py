"""The one true callable entry point."""
import sys
from amatak.bin.amatak_cli import AmatakCLI

def amatak_main():
    """Handle command line execution."""
    cli = AmatakCLI()
    
    # Handle version flag directly
    if '--version' in sys.argv or '-v' in sys.argv:
        cli.print_version()
        return 0
    
    return cli.main()  # Don't pass args here