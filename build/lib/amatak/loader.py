import os
import sys
import importlib.util
import importlib.abc
import warnings
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Union

class AmatakLoader(importlib.abc.Loader):
    """Enhanced Amatak loader with proper syntax and error handling"""
    
    def __init__(self, path: str):
        self.path = Path(path)
        self.type_map = {
            'nil': 'None',
            'true': 'True',
            'false': 'False',
            'catch': 'except',
            'array': 'List',
            'dict': 'Dict',
            'string': 'str',
            'int': 'int',
            'float': 'float',
            'bool': 'bool',
            'any': 'Any',
            'optional': 'Optional',
            'union': 'Union'
        }
        self._exports: Set[str] = set()
        self._imports: List[str] = []
        self._current_class: Optional[str] = None

    def create_module(self, spec):
        return None  # Use default module creation

    def exec_module(self, module):
        if not self.path.exists():
            raise ImportError(f"Amatak file not found: {self.path}")
            
        # Add defined() function to the module's namespace
        module.__dict__['defined'] = lambda name: name in module.__dict__ or name in globals()
        
        with open(self.path, 'r', encoding='utf-8') as f:
            amatak_code = f.read()
        
        try:
            python_code = self._transpile_amatak(amatak_code)
            exec(python_code, module.__dict__)
            
            if self._exports:
                module.__dict__['__all__'] = list(self._exports)
                
        except Exception as e:
            raise ImportError(f"Error executing Amatak code from {self.path}: {str(e)}") from e

    def _transpile_amatak(self, code: str) -> str:
        """Convert Amatak code to Python"""
        lines = []
        in_multiline_comment = False
        
        for line in code.split('\n'):
            line = line.rstrip()
            
            if '/*' in line:
                in_multiline_comment = True
            if '*/' in line:
                in_multiline_comment = False
                continue
            if in_multiline_comment or not line.strip() or line.strip().startswith('#'):
                continue
                
            processed_line = self._process_line(line)
            if processed_line is not None:
                lines.append(processed_line)
                
        if self._imports:
            lines.insert(0, '\n'.join(sorted(set(self._imports))))
            
        return '\n'.join(lines)

    def _process_line(self, line: str) -> Optional[str]:
        """Process individual line of Amatak code"""
        if line.strip().startswith('export '):
            exports = [x.strip() for x in line[7:].split(' and ')]
            self._exports.update(exports)
            return None
            
        if 'from python' in line:
            self._imports.append(line.replace('from python', '').strip())
            return None
            
        if line.startswith('class '):
            self._current_class = line.split()[1].split('(')[0]
            
        for amatak_type, py_type in self.type_map.items():
            line = line.replace(amatak_type, py_type)
            
        if 'def ' in line and ':' in line and ') ->' not in line:
            line = line.replace('):', ') -> None:')
            
        return line.replace('&&', 'and').replace('||', 'or')
    

    def load_amatak_module(path: str):
        """Load .amatak file as Python module with relative import support"""
        from pathlib import Path
        import importlib.util
        import sys
        
        path = Path(path)
        module_name = path.stem
        
        # Add parent directory to path for relative imports
        sys.path.insert(0, str(path.parent))
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            return module
        finally:
            # Clean up path
            if str(path.parent) in sys.path:
                sys.path.remove(str(path.parent))

class AmatakFinder(importlib.abc.MetaPathFinder):
    """Finder implementation for Amatak files"""
    
    def __init__(self):
        self._found_paths: Dict[str, Path] = {}
        self._searched_paths: Set[Path] = set()

    def find_spec(self, fullname, path, target=None):
        if path is None:
            path = sys.path
            
        parts = fullname.split('.')
        possible_names = [f"{parts[-1]}.amatak", "__init__.amatak"]
        
        for entry in map(Path, path):
            try:
                if entry in self._searched_paths:
                    continue
                    
                self._searched_paths.add(entry)
                
                for name in possible_names:
                    amatak_path = entry / name
                    if amatak_path.exists():
                        self._found_paths[fullname] = amatak_path
                        return importlib.util.spec_from_file_location(
                            fullname,
                            amatak_path,
                            loader=AmatakLoader(amatak_path),
                            submodule_search_locations=[str(entry)]
                        )
            except (TypeError, OSError) as e:
                continue
                
        return None

def load_module(module_path: Union[str, Path]) -> Any:
    """Public interface to load modules"""
    loader = AmatakLoader(Path(module_path))
    spec = importlib.util.spec_from_file_location(
        Path(module_path).stem,
        module_path,
        loader=loader
    )
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module

def clear_cache() -> None:
    """Clear loader cache"""
    global _amatak_loader_cache
    _amatak_loader_cache = {}

def install_loader(priority: int = 0) -> None:
    """Install the Amatak import hook"""
    if not any(isinstance(finder, AmatakFinder) for finder in sys.meta_path):
        sys.meta_path.insert(priority, AmatakFinder())

def uninstall_loader() -> None:
    """Remove the Amatak import hook"""
    sys.meta_path = [finder for finder in sys.meta_path 
                    if not isinstance(finder, AmatakFinder)]

# Export public API
__all__ = ['AmatakLoader', 'AmatakFinder', 'load_module', 'clear_cache', 'install_loader', 'uninstall_loader']

# Install by default with medium priority
install_loader(priority=1)