import re
from typing import Callable, Dict, Any
from ..error_handling import error_handler

class SecurityMiddleware:
    """Security middleware for input validation and protection"""
    
    def __init__(self):
        self.sanitize_patterns = [
            (re.compile(r'<script.*?>.*?</script>', re.IGNORECASE), ''),  # XSS
            (re.compile(r'--'), ''),  # SQL comments
            (re.compile(r';'), ''),  # SQL injection
            (re.compile(r'\b(?:DROP|DELETE|TRUNCATE)\b', re.IGNORECASE), '[REDACTED]')  # SQL keywords
        ]
        
    def sanitize_input(self, input_data: Any) -> Any:
        """Sanitize input data"""
        if isinstance(input_data, str):
            for pattern, replacement in self.sanitize_patterns:
                input_data = pattern.sub(replacement, input_data)
        elif isinstance(input_data, dict):
            return {k: self.sanitize_input(v) for k, v in input_data.items()}
        elif isinstance(input_data, list):
            return [self.sanitize_input(item) for item in input_data]
        return input_data

    def secure_operation(self, func: Callable) -> Callable:
        """Decorator to secure operations with input validation"""
        def wrapped(*args, **kwargs):
            try:
                # Sanitize all inputs
                clean_args = [self.sanitize_input(arg) for arg in args]
                clean_kwargs = {k: self.sanitize_input(v) for k, v in kwargs.items()}
                
                # Rate limiting check
                if not self._check_rate_limit(func.__name__):
                    raise SecurityError("Rate limit exceeded")
                
                return func(*clean_args, **clean_kwargs)
            except Exception as e:
                error_handler.log_error(e, {
                    "operation": func.__name__,
                    "type": "security_middleware"
                })
                raise
        return wrapped

    def _check_rate_limit(self, operation: str) -> bool:
        """Basic rate limiting implementation"""
        # TODO: Implement proper rate limiting
        return True

class SecurityError(Exception):
    """Specialized security exception"""
    pass

# Global security middleware instance
security_middleware = SecurityMiddleware()