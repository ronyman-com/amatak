import os
import warnings

# First try Python imports
try:
    from .drivers import BaseDriver, SQLiteDriver, PostgresDriver
    DRIVERS_AVAILABLE = True
except ImportError as e:
    DRIVERS_AVAILABLE = False
    warnings.warn(f"Database drivers not available: {e}", RuntimeWarning)
    BaseDriver = SQLiteDriver = PostgresDriver = None

# Then try Amatak imports as fallback
if not DRIVERS_AVAILABLE:
    try:
        from ..loader import load_amatak_module
        BaseDriver = load_amatak_module(str(Path(__file__).parent / 'drivers' / 'base_driver.amatak'))
        SQLiteDriver = load_amatak_module(str(Path(__file__).parent / 'drivers' / 'sqlite.amatak'))
        PostgresDriver = load_amatak_module(str(Path(__file__).parent / 'drivers' / 'postgres.amatak'))
        DRIVERS_AVAILABLE = all([BaseDriver, SQLiteDriver, PostgresDriver])
    except Exception as e:
        warnings.warn(f"Failed to load Amatak drivers: {e}", RuntimeWarning)

# ORM imports
try:
    from .orm import (
        Model,
        Field,
        IntegerField,
        StringField,
        BooleanField,
        FloatField,
        DateTimeField,
        ForeignKey
    )
    ORM_AVAILABLE = True
except ImportError as e:
    ORM_AVAILABLE = False
    warnings.warn(f"ORM not available: {e}", RuntimeWarning)
    Model = Field = IntegerField = StringField = BooleanField = None
    FloatField = DateTimeField = ForeignKey = None

def connect(db_type: str, **params):
    """Connect to database with automatic driver selection"""
    if not DRIVERS_AVAILABLE:
        raise RuntimeError("No database drivers available")
    
    try:
        if db_type == 'sqlite':
            driver = SQLiteDriver()
            driver.connect(**params)
            return driver
        elif db_type == 'postgres':
            driver = PostgresDriver()
            driver.connect(**params)
            return driver
        else:
            raise ValueError(f"Unsupported database type: {db_type}")
    except Exception as e:
        raise RuntimeError(f"Connection failed: {e}")

__all__ = ['connect']
if DRIVERS_AVAILABLE:
    __all__.extend(['BaseDriver', 'SQLiteDriver', 'PostgresDriver'])
if ORM_AVAILABLE:
    __all__.extend([
        'Model', 'Field', 'IntegerField', 'StringField',
        'BooleanField', 'FloatField', 'DateTimeField', 'ForeignKey'
    ])