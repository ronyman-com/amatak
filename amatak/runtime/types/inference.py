from typing import Dict, List, Optional, Union
from .core import (
    AmatakType, DynamicType, IntegerType, FloatType, StringType, 
    BooleanType, ArrayType, ObjectType, FunctionType, NullableType,
    is_type, type_of
)
from ..errors import AmatakTypeError

class TypeInferrer:
    """Performs type inference and validation across the language runtime"""
    
    def __init__(self):
        self._type_cache: Dict[str, AmatakType] = {}
        self._current_scope = 0
        self._scopes: List[Dict[str, AmatakType]] = [{}]
    
    def enter_scope(self):
        """Push a new type scope"""
        self._current_scope += 1
        self._scopes.append({})
    
    def exit_scope(self):
        """Pop the current type scope"""
        if self._current_scope == 0:
            raise AmatakTypeError("Cannot exit global scope")
        self._scopes.pop()
        self._current_scope -= 1
    
    def declare_variable(self, name: str, type: AmatakType):
        """Declare a variable with a specific type in current scope"""
        if name in self._scopes[self._current_scope]:
            raise AmatakTypeError(f"Variable '{name}' already declared in this scope")
        self._scopes[self._current_scope][name] = type
    
    def get_variable_type(self, name: str) -> AmatakType:
        """Get the type of a variable by searching through scopes"""
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        raise AmatakTypeError(f"Undefined variable: {name}")
    
    def infer_literal(self, value: Any) -> AmatakType:
        """Infer the type of a literal value"""
        if value is None:
            return NullableType(DynamicType())
        return type_of(value)
    
    def infer_binary_op(self, 
                       left_type: AmatakType, 
                       op: str, 
                       right_type: AmatakType) -> AmatakType:
        """Infer the result type of a binary operation"""
        # Numeric operations
        if op in {'+', '-', '*', '/', '%'}:
            if isinstance(left_type, (IntegerType, FloatType)) and \
               isinstance(right_type, (IntegerType, FloatType)):
                # Promote to float if either operand is float
                if isinstance(left_type, FloatType) or isinstance(right_type, FloatType):
                    return FloatType()
                return IntegerType()
            # String concatenation
            if op == '+' and isinstance(left_type, StringType) and isinstance(right_type, StringType):
                return StringType()
            raise AmatakTypeError(f"Invalid operands for {op}: {left_type} and {right_type}")
        
        # Comparison operations
        if op in {'==', '!=', '<', '>', '<=', '>='}:
            if left_type == right_type or (
                isinstance(left_type, (IntegerType, FloatType)) and 
                isinstance(right_type, (IntegerType, FloatType))
            ):
                return BooleanType()
            raise AmatakTypeError(f"Cannot compare {left_type} and {right_type} with {op}")
        
        # Logical operations
        if op in {'&&', '||'}:
            if isinstance(left_type, BooleanType) and isinstance(right_type, BooleanType):
                return BooleanType()
            raise AmatakTypeError(f"Logical {op} requires boolean operands")
        
        raise AmatakTypeError(f"Unknown binary operator: {op}")
    
    def infer_unary_op(self, op: str, operand_type: AmatakType) -> AmatakType:
        """Infer the result type of a unary operation"""
        if op == '-':
            if isinstance(operand_type, (IntegerType, FloatType)):
                return operand_type
            raise AmatakTypeError(f"Cannot apply {op} to {operand_type}")
        if op == '!':
            if isinstance(operand_type, BooleanType):
                return BooleanType()
            raise AmatakTypeError(f"Cannot apply {op} to {operand_type}")
        raise AmatakTypeError(f"Unknown unary operator: {op}")
    
    def infer_call(self, 
                  func_type: AmatakType, 
                  arg_types: List[AmatakType]) -> AmatakType:
        """Infer the return type of a function call"""
        if not isinstance(func_type, FunctionType):
            raise AmatakTypeError(f"Cannot call non-function type: {func_type}")
        
        if len(arg_types) != len(func_type.params):
            raise AmatakTypeError(
                f"Expected {len(func_type.params)} arguments, got {len(arg_types)}")
        
        for i, (arg_type, param_type) in enumerate(zip(arg_types, func_type.params)):
            if not self.is_subtype(arg_type, param_type):
                raise AmatakTypeError(
                    f"Argument {i} type mismatch: expected {param_type}, got {arg_type}")
        
        return func_type.return_type
    
    def infer_array_access(self, 
                         array_type: AmatakType, 
                         index_type: AmatakType) -> AmatakType:
        """Infer the type of an array access operation"""
        if not isinstance(array_type, ArrayType):
            raise AmatakTypeError(f"Cannot index into non-array type: {array_type}")
        if not isinstance(index_type, IntegerType):
            raise AmatakTypeError(f"Array index must be integer, got {index_type}")
        return array_type.element_type
    
    def infer_member_access(self,
                          object_type: AmatakType,
                          member_name: str) -> AmatakType:
        """Infer the type of an object member access"""
        if not isinstance(object_type, ObjectType):
            raise AmatakTypeError(f"Cannot access member of non-object type: {object_type}")
        if member_name not in object_type.fields:
            raise AmatakTypeError(f"Object has no member '{member_name}'")
        return object_type.fields[member_name]
    
    def is_subtype(self, subtype: AmatakType, supertype: AmatakType) -> bool:
        """Check if one type is a subtype of another"""
        # Every type is a subtype of Dynamic
        if isinstance(supertype, DynamicType):
            return True
        
        # Nullable types
        if isinstance(subtype, NullableType):
            if not isinstance(supertype, NullableType):
                return False
            return self.is_subtype(subtype.base_type, supertype.base_type)
        
        # Exact type match
        if type(subtype) == type(supertype):
            # Handle numeric types
            if isinstance(subtype, (IntegerType, FloatType)):
                # Check value constraints
                if (isinstance(supertype, IntegerType) and 
                    isinstance(subtype, IntegerType)):
                    return (
                        (supertype.min is None or subtype.min >= supertype.min) and
                        (supertype.max is None or subtype.max <= supertype.max)
                # Int is subtype of Float
                if isinstance(subtype, IntegerType) and isinstance(supertype, FloatType):
                    return True
                # Float is not subtype of Int
                return False
            
            # Arrays with compatible element types
            if isinstance(subtype, ArrayType) and isinstance(supertype, ArrayType):
                return self.is_subtype(subtype.element_type, supertype.element_type)
            
            # Objects with compatible fields
            if isinstance(subtype, ObjectType) and isinstance(supertype, ObjectType):
                return all(
                    name in supertype.fields and 
                    self.is_subtype(subtype.fields[name], supertype.fields[name])
                    for name in supertype.fields
                )
            
            # Functions with compatible signatures
            if isinstance(subtype, FunctionType) and isinstance(supertype, FunctionType):
                if len(subtype.params) != len(supertype.params):
                    return False
                return (
                    all(self.is_subtype(supertype.params[i], subtype.params[i]) 
                        for i in range(len(subtype.params))) and
                    self.is_subtype(subtype.return_type, supertype.return_type)
                )
            
            # Simple types with no special constraints
            return True
        
        # Special case: Int is subtype of Float
        if isinstance(subtype, IntegerType) and isinstance(supertype, FloatType):
            return True
            
        return False
    
    def unify_types(self, *types: AmatakType) -> AmatakType:
        """Find the most specific common supertype of multiple types"""
        if not types:
            return DynamicType()
        
        # Start with the first type
        result = types[0]
        
        # Find common supertype with each remaining type
        for t in types[1:]:
            if self.is_subtype(result, t):
                # Current result is subtype - keep it
                continue
            elif self.is_subtype(t, result):
                # New type is subtype - use it
                result = t
            else:
                # No subtype relationship - fall back to dynamic
                return DynamicType()
        
        return result
    
    def validate_assignment(self, 
                          target_type: AmatakType, 
                          value_type: AmatakType) -> bool:
        """Check if a value can be assigned to a target"""
        # Allow assignment to dynamic type
        if isinstance(target_type, DynamicType):
            return True
        
        # Handle nullable types
        if isinstance(target_type, NullableType):
            if isinstance(value_type, NullableType):
                return self.is_subtype(value_type.base_type, target_type.base_type)
            return self.is_subtype(value_type, target_type.base_type)
        
        # Normal subtype check
        return self.is_subtype(value_type, target_type)