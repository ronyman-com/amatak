import os
import sys
import zipfile
from pathlib import Path
import shutil

def install_amatak():
    try:
        # Determine install location
        install_path = Path.home() / '.amatak'
        install_path.mkdir(exist_ok=True)
        
        # Create directory structure
        (install_path / 'lib').mkdir(exist_ok=True)
        stdlib_path = install_path / 'stdlib'
        stdlib_path.mkdir(exist_ok=True)
        (install_path / 'bin').mkdir(exist_ok=True)
        
        # Try to locate stdlib files
        source_stdlib = Path(__file__).parent / 'stdlib'
        if source_stdlib.exists():
            print(f"Copying stdlib from {source_stdlib}")
            shutil.copytree(source_stdlib, stdlib_path, dirs_exist_ok=True)
        else:
            print("No stdlib found - creating empty standard library directory")
            (stdlib_path / '__init__.py').touch()
        
        # Create launcher scripts
        create_launcher_script(install_path)
        
        print(f"\nAmatak successfully installed to: {install_path}")
        print("Please add the following to your PATH:")
        print(f"    {install_path / 'bin'}\n")
        
    except Exception as e:
        print(f"\nInstallation failed: {str(e)}", file=sys.stderr)
        sys.exit(1)

def create_launcher_script(install_path):
    launcher = f"""#!/usr/bin/env python3
import os
import sys

os.environ['AMATAK_HOME'] = r'{install_path}'
os.execvp('python', ['python', '-m', 'amatak'] + sys.argv[1:])
"""
    
    # Create Unix launcher
    with open(install_path / 'bin' / 'amatak', 'w', encoding='utf-8') as f:
        f.write(launcher)
    os.chmod(install_path / 'bin' / 'amatak', 0o755)
    
    # Create Windows launcher
    with open(install_path / 'bin' / 'amatak.bat', 'w', encoding='utf-8') as f:
        f.write(f"""@echo off
set AMATAK_HOME={install_path}
python -m amatak %*
""")

if __name__ == '__main__':
    install_amatak()