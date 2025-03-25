from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, Union
from ..errors import AmatakTypeError

@dataclass
class AmatakType:
    """Base type for all Amatak types"""
    name: str
    default: Any = None
    constraints: List[Any] = field(default_factory=list)
    
    def validate(self, value: Any) -> bool:
        """Validate if a value matches this type"""
        return True
    
    def coerce(self, value: Any) -> Any:
        """Coerce a value to this type if possible"""
        return value
    
    def __str__(self) -> str:
        return self.name

class DynamicType(AmatakType):
    """Type that accepts any value (dynamic typing)"""
    def __init__(self):
        super().__init__("Dynamic", None)
    
    def validate(self, value: Any) -> bool:
        return True

class IntegerType(AmatakType):
    """Integer numeric type"""
    def __init__(self, min_val: Optional[int] = None, max_val: Optional[int] = None):
        super().__init__("Integer", 0)
        self.min = min_val
        self.max = max_val
        if min_val is not None:
            self.constraints.append(f"min={min_val}")
        if max_val is not None:
            self.constraints.append(f"max={max_val}")
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, int):
            return False
        if self.min is not None and value < self.min:
            return False
        if self.max is not None and value > self.max:
            return False
        return True
    
    def coerce(self, value: Any) -> int:
        try:
            val = int(value)
            if self.validate(val):
                return val
            raise AmatakTypeError(f"Value {val} out of bounds for {self}")
        except (ValueError, TypeError):
            raise AmatakTypeError(f"Cannot convert {value} to Integer")

class FloatType(AmatakType):
    """Floating-point numeric type"""
    def __init__(self, min_val: Optional[float] = None, max_val: Optional[float] = None):
        super().__init__("Float", 0.0)
        self.min = min_val
        self.max = max_val
        if min_val is not None:
            self.constraints.append(f"min={min_val}")
        if max_val is not None:
            self.constraints.append(f"max={max_val}")
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, (int, float)):
            return False
        if self.min is not None and value < self.min:
            return False
        if self.max is not None and value > self.max:
            return False
        return True
    
    def coerce(self, value: Any) -> float:
        try:
            val = float(value)
            if self.validate(val):
                return val
            raise AmatakTypeError(f"Value {val} out of bounds for {self}")
        except (ValueError, TypeError):
            raise AmatakTypeError(f"Cannot convert {value} to Float")

class StringType(AmatakType):
    """String type"""
    def __init__(self, max_length: Optional[int] = None, pattern: Optional[str] = None):
        super().__init__("String", "")
        self.max_length = max_length
        self.pattern = pattern
        if max_length is not None:
            self.constraints.append(f"max_len={max_length}")
        if pattern is not None:
            self.constraints.append(f"pattern={pattern}")
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        if self.max_length is not None and len(value) > self.max_length:
            return False
        if self.pattern is not None:
            import re
            if not re.match(self.pattern, value):
                return False
        return True
    
    def coerce(self, value: Any) -> str:
        try:
            val = str(value)
            if self.validate(val):
                return val
            raise AmatakTypeError(f"String {val} violates constraints for {self}")
        except (ValueError, TypeError):
            raise AmatakTypeError(f"Cannot convert {value} to String")

class BooleanType(AmatakType):
    """Boolean type"""
    def __init__(self):
        super().__init__("Boolean", False)
    
    def validate(self, value: Any) -> bool:
        return isinstance(value, bool)
    
    def coerce(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            if value.lower() in ('true', 't', 'yes', 'y', '1'):
                return True
            if value.lower() in ('false', 'f', 'no', 'n', '0'):
                return False
        if isinstance(value, (int, float)):
            return bool(value)
        raise AmatakTypeError(f"Cannot convert {value} to Boolean")

class ArrayType(AmatakType):
    """Array (list) type"""
    def __init__(self, element_type: AmatakType, min_len: Optional[int] = None, max_len: Optional[int] = None):
        super().__init__("Array", [])
        self.element_type = element_type
        self.min_len = min_len
        self.max_len = max_len
        self.constraints.append(f"elements={element_type.name}")
        if min_len is not None:
            self.constraints.append(f"min_len={min_len}")
        if max_len is not None:
            self.constraints.append(f"max_len={max_len}")
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, list):
            return False
        if self.min_len is not None and len(value) < self.min_len:
            return False
        if self.max_len is not None and len(value) > self.max_len:
            return False
        return all(self.element_type.validate(item) for item in value)
    
    def coerce(self, value: Any) -> list:
        if not isinstance(value, (list, tuple)):
            raise AmatakTypeError(f"Cannot convert {value} to Array")
        
        try:
            result = [self.element_type.coerce(item) for item in value]
            if self.min_len is not None and len(result) < self.min_len:
                raise AmatakTypeError(f"Array too short (min {self.min_len})")
            if self.max_len is not None and len(result) > self.max_len:
                raise AmatakTypeError(f"Array too long (max {self.max_len})")
            return result
        except AmatakTypeError as e:
            raise AmatakTypeError(f"Array coercion failed: {str(e)}")

class ObjectType(AmatakType):
    """Structured object type"""
    def __init__(self, fields: Dict[str, AmatakType]):
        super().__init__("Object", {})
        self.fields = fields
        for name, typ in fields.items():
            self.constraints.append(f"{name}: {typ.name}")
    
    def validate(self, value: Any) -> bool:
        if not isinstance(value, dict):
            return False
        return all(
            name in value and typ.validate(value[name])
            for name, typ in self.fields.items()
        )
    
    def coerce(self, value: Any) -> dict:
        if not isinstance(value, dict):
            raise AmatakTypeError(f"Cannot convert {value} to Object")
        
        result = {}
        try:
            for name, typ in self.fields.items():
                if name not in value:
                    raise AmatakTypeError(f"Missing field: {name}")
                result[name] = typ.coerce(value[name])
            return result
        except AmatakTypeError as e:
            raise AmatakTypeError(f"Object coercion failed: {str(e)}")

class FunctionType(AmatakType):
    """Function type"""
    def __init__(self, params: List[AmatakType], return_type: AmatakType):
        super().__init__("Function", None)
        self.params = params
        self.return_type = return_type
        self.constraints.extend([f"param: {p.name}" for p in params])
        self.constraints.append(f"returns: {return_type.name}")
    
    def validate(self, value: Any) -> bool:
        # In Amatak, functions are callable objects
        return callable(value)

class NullableType(AmatakType):
    """Wrapper type that allows None values"""
    def __init__(self, base_type: AmatakType):
        super().__init__(f"Nullable[{base_type.name}]", None)
        self.base_type = base_type
    
    def validate(self, value: Any) -> bool:
        return value is None or self.base_type.validate(value)
    
    def coerce(self, value: Any) -> Any:
        if value is None:
            return None
        return self.base_type.coerce(value)

# Built-in type instances
DYNAMIC = DynamicType()
INTEGER = IntegerType()
FLOAT = FloatType()
STRING = StringType()
BOOLEAN = BooleanType()

def is_type(obj: Any) -> bool:
    """Check if an object is a type instance"""
    return isinstance(obj, AmatakType)

def type_of(value: Any) -> AmatakType:
    """Get the Amatak type for a value"""
    if value is None:
        return NullableType(DYNAMIC)
    if isinstance(value, bool):
        return BOOLEAN
    if isinstance(value, int):
        return INTEGER
    if isinstance(value, float):
        return FLOAT
    if isinstance(value, str):
        return STRING
    if isinstance(value, list):
        if not value:
            return ArrayType(DYNAMIC)
        element_type = type_of(value[0])
        return ArrayType(element_type)
    if isinstance(value, dict):
        if not value:
            return ObjectType({})
        field_types = {k: type_of(v) for k, v in value.items()}
        return ObjectType(field_types)
    if callable(value):
        return FunctionType([], DYNAMIC)
    return DYNAMIC