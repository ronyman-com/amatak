import os
import sys
import zipfile
from pathlib import Path

def install_amatak():
    # Determine install location
    install_path = Path.home() / '.amatak'
    install_path.mkdir(exist_ok=True)
    
    # Create directory structure
    (install_path / 'lib').mkdir(exist_ok=True)
    (install_path / 'stdlib').mkdir(exist_ok=True)
    (install_path / 'bin').mkdir(exist_ok=True)
    
    # Extract bundled stdlib
    with zipfile.ZipFile(sys.prefix + '/amatak/stdlib.zip') as z:
        z.extractall(install_path / 'stdlib')
    
    # Create launcher scripts
    create_launcher_script(install_path)
    
    print(f"Amatak installed to {install_path}")
    print("Please add ~/.amatak/bin to your PATH")

def create_launcher_script(install_path):
    launcher = f"""#!/bin/sh
export AMATAK_HOME={install_path}
exec python3 -m amatak "$@"
"""
    
    with open(install_path / 'bin' / 'amatak', 'w') as f:
        f.write(launcher)
    os.chmod(install_path / 'bin' / 'amatak', 0o755)

if __name__ == '__main__':
    install_amatak()