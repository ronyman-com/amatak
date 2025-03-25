"""
Python builtins compatibility layer for Amatak
Ensures consistent behavior across Python versions
"""

import sys
from typing import Any, Callable, Iterable, Optional, Union

# Version check
PYTHON_3 = sys.version_info[0] == 3

class AmatakBuiltins:
    """Wrapper for Python builtins with Amatak-specific behavior"""
    
    @staticmethod
    def range(start: int, stop: Optional[int] = None, step: Optional[int] = None) -> Iterable:
        """Enhanced range with safety checks"""
        if stop is None:
            start, stop = 0, start
        if step == 0:
            raise ValueError("range() step cannot be zero")
        return range(start, stop, step or 1)
    
    @staticmethod
    def print(*args: Any, **kwargs: Any) -> None:
        """Modified print function for Amatak"""
        sep = kwargs.get('sep', ' ')
        end = kwargs.get('end', '\n')
        file = kwargs.get('file', sys.stdout)
        
        # Convert all args to strings safely
        output = sep.join(str(arg) for arg in args) + end
        file.write(output)
        file.flush()
    
    @staticmethod
    def input(prompt: str = "") -> str:
        """Enhanced input with validation"""
        while True:
            try:
                if PYTHON_3:
                    return input(prompt)
                else:
                    return raw_input(prompt)  # type: ignore
            except (EOFError, KeyboardInterrupt):
                print("\nInput interrupted")
                raise
    
    @staticmethod
    def len(obj: Any) -> int:
        """Safe length check with Amatak types support"""
        try:
            return len(obj)
        except TypeError:
            if hasattr(obj, '__len__'):
                return obj.__len__()
            raise TypeError(f"Object of type {type(obj)} has no len()")
    
    # Math-related builtins
    @staticmethod
    def abs(x: Union[int, float]) -> Union[int, float]:
        """Absolute value with type preservation"""
        return -x if x < 0 else x
    
    @staticmethod
    def min_max(iterable: Iterable, *, key: Optional[Callable] = None) -> tuple:
        """Single-pass min and max calculation"""
        it = iter(iterable)
        try:
            min_val = max_val = next(it)
        except StopIteration:
            raise ValueError("min_max() arg is an empty sequence")
        
        for item in it:
            if key:
                item_key = key(item)
                if item_key < key(min_val):
                    min_val = item
                if item_key > key(max_val):
                    max_val = item
            else:
                if item < min_val:
                    min_val = item
                if item > max_val:
                    max_val = item
        
        return (min_val, max_val)

# Public interface
range = AmatakBuiltins.range
print = AmatakBuiltins.print
input = AmatakBuiltins.input
len = AmatakBuiltins.len
abs = AmatakBuiltins.abs
min_max = AmatakBuiltins.min_max