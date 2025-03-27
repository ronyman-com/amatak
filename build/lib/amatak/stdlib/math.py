# amatak/stdlib/math.py
"""
Amatak Math Standard Library
Provides mathematical functions and constants
"""

from amatak.error_handling import ErrorHandler
import math
import random

class Math:
    """Math operations with error handling and extended functionality"""
    
    def __init__(self, precision: int = 15):
        self._error_handler = ErrorHandler()
        self.precision = precision
        
        # Constants
        self.PI = math.pi
        self.E = math.e
        self.TAU = math.tau
        self.INF = float('inf')
        self.NAN = float('nan')
        
        # Configure precision
        self._set_precision(precision)
    
    def _set_precision(self, precision: int):
        """Internal method to set calculation precision"""
        self.precision = precision
    
    def abs(self, x):
        """Absolute value"""
        return abs(x)
    
    def floor(self, x):
        """Floor of a number"""
        return math.floor(x)
    
    def ceil(self, x):
        """Ceiling of a number"""
        return math.ceil(x)
    
    def round(self, x, ndigits=None):
        """Round a number"""
        return round(x, ndigits)
    
    def sqrt(self, x):
        """Square root with error checking"""
        if x < 0:
            self._error_handler.log("Cannot calculate square root of negative number")
            raise ValueError("Math domain error")
        return math.sqrt(x)
    
    def pow(self, x, y):
        """Power function"""
        return math.pow(x, y)
    
    def exp(self, x):
        """Exponential function"""
        return math.exp(x)
    
    def log(self, x, base=math.e):
        """Logarithm with error checking"""
        if x <= 0:
            self._error_handler.log("Cannot calculate logarithm of non-positive number")
            raise ValueError("Math domain error")
        return math.log(x, base)
    
    def log10(self, x):
        """Base-10 logarithm"""
        return self.log(x, 10)
    
    def log2(self, x):
        """Base-2 logarithm"""
        return self.log(x, 2)
    
    def sin(self, x):
        """Sine function"""
        return math.sin(x)
    
    def cos(self, x):
        """Cosine function"""
        return math.cos(x)
    
    def tan(self, x):
        """Tangent function"""
        return math.tan(x)
    
    def radians(self, x):
        """Convert degrees to radians"""
        return math.radians(x)
    
    def degrees(self, x):
        """Convert radians to degrees"""
        return math.degrees(x)
    
    def random(self):
        """Random float between 0 and 1"""
        return random.random()
    
    def rand_int(self, a, b):
        """Random integer between a and b (inclusive)"""
        if a > b:
            self._error_handler.log(f"Invalid range for rand_int: {a} > {b}")
            raise ValueError("Invalid range")
        return random.randint(a, b)
    
    def mean(self, data):
        """Arithmetic mean"""
        if not data:
            self._error_handler.log("Cannot calculate mean of empty data")
            raise ValueError("Empty data")
        return sum(data) / len(data)
    
    def median(self, data):
        """Median of data"""
        if not data:
            self._error_handler.log("Cannot calculate median of empty data")
            raise ValueError("Empty data")
            
        sorted_data = sorted(data)
        n = len(sorted_data)
        mid = n // 2
        
        if n % 2 == 1:
            return sorted_data[mid]
        else:
            return (sorted_data[mid - 1] + sorted_data[mid]) / 2
    
    def stdev(self, data):
        """Standard deviation"""
        if len(data) < 2:
            self._error_handler.log("Insufficient data for stdev")
            raise ValueError("Insufficient data")
            
        m = self.mean(data)
        return math.sqrt(sum((x - m) ** 2 for x in data) / (len(data) - 1))
    
    def variance(self, data):
        """Variance"""
        if len(data) < 2:
            self._error_handler.log("Insufficient data for variance")
            raise ValueError("Insufficient data")
            
        m = self.mean(data)
        return sum((x - m) ** 2 for x in data) / (len(data) - 1)
    
    def max(self, *args):
        """Maximum value"""
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            return max(args[0])
        return max(args)
    
    def min(self, *args):
        """Minimum value"""
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            return min(args[0])
        return min(args)
    
    def clamp(self, value, min_val, max_val):
        """Clamp value between min and max"""
        return max(min_val, min(value, max_val))
    
    def lerp(self, a, b, t):
        """Linear interpolation between a and b"""
        return a + (b - a) * t
    
    def is_close(self, a, b, rel_tol=1e-09, abs_tol=0.0):
        """Check if two numbers are close within tolerance"""
        return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)

# Export default math instance
math = Math()