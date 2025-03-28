"""Actual CLI implementation."""
from amatak.bin.amatak_cli import AmatakCLI

def amatak_main():
    """The one true callable entry function."""
    cli = AmatakCLI()
    return cli.main()