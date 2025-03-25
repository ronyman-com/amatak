"""
Python stdlib compatibility layer for Amatak
Organized by module functionality
"""

import os
import sys
from typing import Any, Dict, List, Optional, Tuple

# Version-specific imports
if sys.version_info[0] == 3:
    from urllib.parse import urlparse, urlunparse
else:
    from urlparse import urlparse, urlunparse  # type: ignore

class PathCompat:
    """os.path compatibility layer"""
    
    @staticmethod
    def join(*parts: str) -> str:
        """Safe path joining"""
        return os.path.join(*parts).replace('\\', '/')
    
    @staticmethod
    def exists(path: str) -> bool:
        """Path existence check with normalization"""
        return os.path.exists(path.replace('/', os.sep))

class URLCompat:
    """URL handling compatibility"""
    
    @staticmethod
    def parse(url: str) -> Tuple[str, str, str, str, str, str]:
        """URL parsing with consistent return types"""
        return urlparse(url)
    
    @staticmethod
    def unparse(components: Tuple[str, str, str, str, str, str]) -> str:
        """URL reconstruction"""
        return urlunparse(components)

class MathCompat:
    """Math operations compatibility"""
    
    @staticmethod
    def ceil(x: float) -> int:
        """Consistent ceiling across Python versions"""
        import math
        return int(math.ceil(x))
    
    @staticmethod
    def factorial(n: int) -> int:
        """Factorial with validation"""
        if n < 0:
            raise ValueError("Factorial of negative number")
        result = 1
        for i in range(1, n+1):
            result *= i
        return result

# Public API
path = PathCompat()
url = URLCompat()
math = MathCompat()