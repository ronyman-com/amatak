"""Python CLI entry point - must only contain this function."""
from amatak.bin.amatak_cli import AmatakCLI

def amatak_cli_entry():
    """The only callable entry point."""
    cli = AmatakCLI()
    return cli.main()

# Nothing else should be in this file