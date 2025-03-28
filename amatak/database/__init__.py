"""
Amatak Database Package
"""

import os
import sys
import warnings
from pathlib import Path
from typing import Optional, Union

try:
    from ..loader import load_amatak_module
    AMATAK_LOADER = True
except ImportError as e:
    AMATAK_LOADER = False
    warnings.warn(f"Loader not available: {e}", RuntimeWarning)

def _load_driver(name: str):
    """Load driver with improved class detection"""
    # Try Python implementation first
    try:
        py_module = __import__(f'amatak.database.drivers.{name}', fromlist=['*'])
        # Look for both naming conventions
        driver_class = (
            getattr(py_module, f'{name.capitalize()}Driver', None) or
            getattr(py_module, f'{name}Driver', None) or
            next((v for k,v in py_module.__dict__.items() 
                 if k.lower().endswith('driver') and isinstance(v, type)), None)
        )
        if driver_class:
            return driver_class
    except ImportError:
        pass
    
    # Fall back to Amatak implementation
    if AMATAK_LOADER:
        try:
            driver_path = str(Path(__file__).parent / 'drivers' / f'{name}.amatak')
            if os.path.exists(driver_path):
                module = load_amatak_module(driver_path)
                
                # More flexible class detection
                driver_class = None
                for class_name in [
                    f'{name.capitalize()}Driver',
                    f'{name}Driver',
                    'BaseDriver' if name == 'base_driver' else None
                ]:
                    if class_name and hasattr(module, class_name):
                        driver_class = getattr(module, class_name)
                        break
                
                # Fallback: Find any class ending with Driver
                if not driver_class:
                    for attr_name, attr_value in module.__dict__.items():
                        if attr_name.endswith('Driver') and isinstance(attr_value, type):
                            driver_class = attr_value
                            break
                
                if driver_class:
                    return driver_class
                
                warnings.warn(
                    f"Driver class not found in {name}.amatak. "
                    f"Available: {[k for k in dir(module) if not k.startswith('_')]}",
                    RuntimeWarning
                )
        except Exception as e:
            warnings.warn(
                f"Failed to load Amatak driver {name}: {type(e).__name__}: {str(e)}",
                RuntimeWarning
            )
    
    return None

# Load drivers with flexible naming
BaseDriver = _load_driver('base_driver') or _load_driver('base')
SQLiteDriver = _load_driver('sqlite')
PostgresDriver = _load_driver('postgres')

DRIVERS_AVAILABLE = all([BaseDriver, SQLiteDriver, PostgresDriver])

# Load drivers with better error reporting
try:
    BaseDriver = _load_driver('base_driver')
    SQLiteDriver = _load_driver('sqlite')
    PostgresDriver = _load_driver('postgres')
    DRIVERS_AVAILABLE = all([BaseDriver, SQLiteDriver, PostgresDriver])
except Exception as e:
    DRIVERS_AVAILABLE = False
    warnings.warn(f"Critical driver loading error: {e}", RuntimeWarning)

def connect(db_type: str, **params) -> Optional[Union['SQLiteDriver', 'PostgresDriver']]:
    """Create and return a database connection with validation"""
    if not DRIVERS_AVAILABLE:
        warnings.warn("Database drivers not available", RuntimeWarning)
        return None
    
    try:
        if db_type == 'sqlite':
            if SQLiteDriver:
                driver = SQLiteDriver()
                if hasattr(driver, 'connect') and callable(driver.connect):
                    if driver.connect(**params):
                        return driver
        elif db_type == 'postgres':
            if PostgresDriver:
                driver = PostgresDriver()
                if hasattr(driver, 'connect') and callable(driver.connect):
                    if driver.connect(**params):
                        return driver
        else:
            warnings.warn(f"Unsupported database type: {db_type}", RuntimeWarning)
    except Exception as e:
        warnings.warn(f"Connection failed: {e}", RuntimeWarning)
    
    return None

__all__ = ['connect', 'BaseDriver', 'SQLiteDriver', 'PostgresDriver']