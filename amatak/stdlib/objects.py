# Amatak Object Utilities
# Object manipulation and introspection tools

import inspect
import copy
from typing import Any, Dict, List
from amatak.error_handling import ErrorHandler
from amatak.security.middleware import SecurityMiddleware

class Objects:
    """Object manipulation and introspection utilities"""
    
    def __init__(self):
        self.error_handler = ErrorHandler()
        self.security = SecurityMiddleware()
        
    def deep_copy(self, obj: Any) -> Any:
        """Create deep copy with security checks"""
        self.security.validate_object(obj)
        return copy.deepcopy(obj)
        
    def shallow_copy(self, obj: Any) -> Any:
        """Create shallow copy"""
        return copy.copy(obj)
        
    def get_attributes(self, obj: Any) -> Dict[str, Any]:
        """Get all attributes of an object"""
        return vars(obj)
        
    def has_method(self, obj: Any, method_name: str) -> bool:
        """Check if object has specified method"""
        return callable(getattr(obj, method_name, None))
        
    def get_methods(self, obj: Any) -> List[str]:
        """Get all callable methods of an object"""
        return [
            name for name, value in inspect.getmembers(obj) 
            if inspect.ismethod(value) or inspect.isfunction(value)
        ]
        
    def get_properties(self, obj: Any) -> List[str]:
        """Get all properties of an object"""
        return [
            name for name, value in inspect.getmembers(obj.__class__)
            if isinstance(value, property)
        ]
        
    def is_serializable(self, obj: Any) -> bool:
        """Check if object can be JSON serialized"""
        try:
            import json
            json.dumps(obj)
            return True
        except (TypeError, OverflowError):
            return False
            
    def merge(self, target: Dict, source: Dict, deep: bool = False) -> Dict:
        """
        Merge two dictionaries
        
        Args:
            target: Dictionary to merge into
            source: Dictionary to merge from
            deep: Perform deep merge if True
        """
        if not deep:
            return {**target, **source}
            
        result = target.copy()
        for key, value in source.items():
            if (key in result and isinstance(result[key], dict) 
                    and isinstance(value, dict)):
                result[key] = self.merge(result[key], value, deep=True)
            else:
                result[key] = value
        return result
        
    def apply_defaults(self, obj: Dict, defaults: Dict) -> Dict:
        """Apply default values to dictionary"""
        return {**defaults, **obj}
        
    def freeze(self, obj: Any) -> Any:
        """Make object immutable"""
        if isinstance(obj, dict):
            return frozendict(obj)
        elif isinstance(obj, list):
            return tuple(obj)
        return obj
        
    def memoize(self, func):
        """Memoization decorator"""
        cache = {}
        
        def wrapper(*args, **kwargs):
            key = (args, frozenset(kwargs.items()))
            if key not in cache:
                cache[key] = func(*args, **kwargs)
            return cache[key]
            
        return wrapper
        
    def validate_schema(self, obj: Any, schema: Dict) -> bool:
        """Validate object against schema"""
        if isinstance(schema, type):
            return isinstance(obj, schema)
            
        if not isinstance(schema, dict):
            return False
            
        for key, val_schema in schema.items():
            if key not in obj:
                return False
            if not self.validate_schema(obj[key], val_schema):
                return False
        return True

class frozendict(dict):
    """Immutable dictionary implementation"""
    
    def __setitem__(self, key, value):
        raise TypeError("frozendict is immutable")
        
    def __delitem__(self, key):
        raise TypeError("frozendict is immutable")
        
    def clear(self):
        raise TypeError("frozendict is immutable")
        
    def pop(self, key, default=None):
        raise TypeError("frozendict is immutable")
        
    def popitem(self):
        raise TypeError("frozendict is immutable")
        
    def update(self, other):
        raise TypeError("frozendict is immutable")

# Export default objects instance
objects = Objects()