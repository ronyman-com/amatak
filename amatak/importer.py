import os
import sys
import importlib.util
import importlib.abc
from pathlib import Path

class AmatakLoader(importlib.abc.Loader):
    def __init__(self, path):
        self.path = path

    def create_module(self, spec):
        return None  # Use default module creation

    def exec_module(self, module):
        with open(self.path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Here you would normally parse/compile the Amatak code
        # For now we'll just exec it as Python (for demonstration)
        exec(code, module.__dict__)

class AmatakFinder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path, target=None):
        if path is None:
            return None
            
        parts = fullname.split('.')
        basename = parts[-1] + '.amatak'
        
        for entry in path:
            amatak_path = os.path.join(entry, basename)
            if os.path.exists(amatak_path):
                return importlib.util.spec_from_file_location(
                    fullname,
                    amatak_path,
                    loader=AmatakLoader(amatak_path),
                    submodule_search_locations=[]
                )
        return None

# Install the finder
sys.meta_path.append(AmatakFinder())