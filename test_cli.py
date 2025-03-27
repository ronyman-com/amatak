import subprocess
import sys
import os

def test_cli():
    print("Testing direct Python execution...")
    subprocess.run([sys.executable, "amatak/bin/amatak.py", "--version"])
    
    print("\nTesting installed amatak command...")
    subprocess.run(["amatak", "--version"])
    
    if os.name == 'nt':  # Windows
        print("\nTesting batch wrapper...")
        subprocess.run(["./amatak/bin/amatak.bat", "--version"])
    else:  # Unix
        print("\nTesting bash wrapper...")
        subprocess.run(["./amatak/bin/amatak", "--version"])
    
    print("\nTesting module execution...")
    subprocess.run([sys.executable, "-m", "amatak.bin.amatak", "--version"])

if __name__ == "__main__":
    test_cli()