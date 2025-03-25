from typing import Any, Callable
from ....runtime.types.core import (
    IntegerType, FloatType, StringType, BooleanType,
    ArrayType, ObjectType, FunctionType, DynamicType
)
from ....runtime.errors import AmatakTypeError

class PythonToAmatakMarshal:
    """Converts Python objects to Amatak-compatible representations"""
    
    def marshal(self, obj: Any) -> Any:
        """Convert a Python object to Amatak-compatible type"""
        if obj is None:
            return None
        
        # Basic types
        if isinstance(obj, (int, float, str, bool)):
            return obj
        
        # Sequences
        if isinstance(obj, (list, tuple)):
            return [self.marshal(item) for item in obj]
        
        # Dictionaries
        if isinstance(obj, dict):
            return {str(k): self.marshal(v) for k, v in obj.items()}
        
        # Functions and callables
        if callable(obj):
            def wrapped(*args):
                try:
                    result = obj(*[self.unmarshal(arg) for arg in args])
                    return self.marshal(result)
                except Exception as e:
                    raise AmatakRuntimeError(f"Python call failed: {str(e)}")
            return wrapped
        
        # Classes and instances
        if hasattr(obj, '__dict__'):
            return {k: self.marshal(v) for k, v in vars(obj).items() 
                   if not k.startswith('_')}
        
        # Unsupported type
        return str(obj)

class AmatakToPythonMarshal:
    """Converts Amatak objects to Python-compatible representations"""
    
    def unmarshal(self, obj: Any) -> Any:
        """Convert an Amatak object to Python-compatible type"""
        if obj is None:
            return None
            
        # Basic types
        if isinstance(obj, (int, float, str, bool)):
            return obj
            
        # Amatak arrays to Python lists
        if isinstance(obj, list):
            return [self.unmarshal(item) for item in obj]
            
        # Amatak objects to Python dicts
        if isinstance(obj, dict):
            return {k: self.unmarshal(v) for k, v in obj.items()}
            
        # Amatak functions to Python callables
        if callable(obj):
            def wrapped(*args):
                try:
                    result = obj(*[self.marshal(arg) for arg in args])
                    return self.unmarshal(result)
                except Exception as e:
                    raise AmatakRuntimeError(f"Amatak call failed: {str(e)}")
            return wrapped
            
        # Type objects
        if isinstance(obj, type):
            return obj.__name__
            
        # Unsupported type
        return str(obj)

# Singleton instances for convenience
python_to_amatak = PythonToAmatakMarshal()
amatak_to_python = AmatakToPythonMarshal()