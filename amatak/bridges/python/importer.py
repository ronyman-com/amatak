import importlib
import sys
from types import ModuleType
from typing import Any, Dict
from ..errors import AmatakRuntimeError
from .marshal import PythonToAmatakMarshal

class PythonImporter:
    """Handles importing Python modules into Amatak runtime"""
    
    def __init__(self):
        self._marshal = PythonToAmatakMarshal()
        self._imported_modules: Dict[str, ModuleType] = {}
    
    def import_module(self, module_name: str) -> Dict[str, Any]:
        """Import a Python module and make its contents available to Amatak"""
        if module_name in self._imported_modules:
            return self._imported_modules[module_name]
        
        try:
            # Try standard import first
            module = importlib.import_module(module_name)
        except ImportError:
            raise AmatakRuntimeError(f"Python module not found: {module_name}")
        
        # Marshal the module contents to Amatak-compatible types
        marshaled = {
            name: self._marshal.marshal(getattr(module, name))
            for name in dir(module) 
            if not name.startswith('_')
        }
        
        self._imported_modules[module_name] = marshaled
        return marshaled
    
    def import_from(self, module_name: str, names: list[str]) -> Dict[str, Any]:
        """Import specific names from a Python module"""
        module = self.import_module(module_name)
        return {name: module[name] for name in names if name in module}
    
    def register_module(self, name: str, module_dict: Dict[str, Any]):
        """Register a module that can be imported from Amatak code"""
        self._imported_modules[name] = module_dict

    def clear_cache(self):
        """Clear the imported modules cache"""
        self._imported_modules.clear()