# amatak/stdlib/__init__.py
"""Amatak Standard Library

Organizes built-in and installed library modules with dependency management.
"""

import sys
import importlib
import pkgutil
from pathlib import Path
from typing import Dict, Type, Any
from amatak.error_handling import ErrorHandler

# Core standard library modules
CORE_MODULES = {
    'math': '.math',
    'strings': '.strings',
    'fileio': '.fileio',
    'objects': '.objects',
    'containers': {
        'array': '.containers.array',
        'dict': '.containers.dict'
    }
}

class StdlibManager:
    """Manages standard library modules and installed dependencies"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self._loaded_modules: Dict[str, Any] = {}
        self._installed_deps: Dict[str, Any] = {}
        self._init_core_modules()
        self._load_installed_deps()
        
    def _init_core_modules(self) -> None:
        """Initialize core standard library modules"""
        for name, path in CORE_MODULES.items():
            if isinstance(path, dict):
                # Handle submodules
                submodules = {}
                for sub_name, sub_path in path.items():
                    try:
                        module = self._import_module(sub_path, f"amatak.stdlib{sub_path}")
                        submodules[sub_name] = module
                    except ImportError as e:
                        self.error_handler.log(f"Failed to load stdlib module {sub_name}: {e}")
                self._loaded_modules[name] = type(name, (), submodules)
            else:
                try:
                    self._loaded_modules[name] = self._import_module(path, f"amatak.stdlib{path}")
                except ImportError as e:
                    self.error_handler.log(f"Failed to load stdlib module {name}: {e}")

    def _import_module(self, relative_path: str, full_path: str) -> Any:
        """Import a module with error handling"""
        try:
            module = importlib.import_module(full_path, 'amatak.stdlib')
            return module
        except ImportError:
            # Fallback to direct import
            from importlib import import_module
            return import_module(relative_path, 'amatak.stdlib')
            
    def _load_installed_deps(self) -> None:
        """Load installed dependencies from requirements.txt"""
        req_file = Path(__file__).parent.parent.parent / 'requirements.txt'
        if not req_file.exists():
            return
            
        try:
            with open(req_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        pkg_name = line.split('==')[0].split('>')[0].split('<')[0]
                        try:
                            self._installed_deps[pkg_name] = importlib.import_module(pkg_name)
                        except ImportError as e:
                            self.error_handler.log(f"Failed to load dependency {pkg_name}: {e}")
        except Exception as e:
            self.error_handler.log(f"Error reading requirements.txt: {e}")

    def get_module(self, name: str) -> Any:
        """Get a standard library module by name"""
        if name in self._loaded_modules:
            return self._loaded_modules[name]
        if name in self._installed_deps:
            return self._installed_deps[name]
        raise ImportError(f"Module '{name}' not found in stdlib or installed dependencies")

    def __getattr__(self, name: str) -> Any:
        """Attribute access to modules"""
        try:
            return self.get_module(name)
        except ImportError as e:
            raise AttributeError(str(e)) from None

# Initialize the standard library manager
stdlib = StdlibManager()

# Export the main modules directly
math = stdlib.get_module('math')
strings = stdlib.get_module('strings')
fileio = stdlib.get_module('fileio')
objects = stdlib.get_module('objects')
containers = stdlib.get_module('containers')

# Make the manager available
manager = stdlib

# Clean up namespace
del StdlibManager, sys, importlib, pkgutil, Path, Dict, Type, Any, ErrorHandler

# Export the public API
__all__ = [
    'math',
    'strings',
    'fileio',
    'objects',
    'containers',
    'manager',
    'stdlib'
]