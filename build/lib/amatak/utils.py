import os
from pathlib import Path
from typing import Optional
from .errors import AmatakRuntimeError

def load_lib(lib_name: str, lib_dir: Optional[str] = None) -> str:
    """
    Load a library file from the lib directory.
    
    Args:
        lib_name: Name of the library (without extension)
        lib_dir: Optional custom library directory path
        
    Returns:
        str: Contents of the library file
        
    Raises:
        AmatakRuntimeError: If library file cannot be found or read
    """
    try:
        # Determine library directory
        if lib_dir is None:
            # Default to package-relative lib directory
            base_dir = Path(__file__).parent.parent
            lib_path = base_dir / "lib" / f"{lib_name}.amatak"
        else:
            # Use custom library directory
            lib_path = Path(lib_dir) / f"{lib_name}.amatak"
        
        # Verify path is safe
        if not lib_path.resolve().is_relative_to(Path.cwd()):
            raise AmatakRuntimeError(f"Invalid library path: {lib_path}")
        
        # Read file with explicit encoding
        with open(lib_path, "r", encoding="utf-8") as f:
            return f.read()
            
    except FileNotFoundError:
        raise AmatakRuntimeError(
            f"Library '{lib_name}' not found in {lib_path.parent}"
        )
    except PermissionError:
        raise AmatakRuntimeError(
            f"Insufficient permissions to read library: {lib_path}"
        )
    except UnicodeDecodeError:
        raise AmatakRuntimeError(
            f"Could not decode library file (must be UTF-8): {lib_path}"
        )
    except Exception as e:
        raise AmatakRuntimeError(
            f"Unexpected error loading library '{lib_name}': {str(e)}"
        )

def find_libs() -> list[str]:
    """
    Discover available libraries in the lib directory.
    
    Returns:
        list[str]: List of available library names (without extensions)
    """
    lib_dir = Path(__file__).parent.parent / "lib"
    if not lib_dir.exists():
        return []
    
    return [
        f.stem for f in lib_dir.glob("*.amatak") 
        if f.is_file() and f.suffix == ".amatak"
    ]