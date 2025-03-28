from datetime import datetime

class AmatakError(Exception):
    """Base class for all Amatak errors with context and timestamp support."""
    
    def __init__(self, message: str, context: dict = None):
        """
        Initialize the error with a message and optional context.
        
        Args:
            message: Error description
            context: Additional context dictionary (default: None)
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}
        self.timestamp = datetime.utcnow().isoformat()
        
    def __str__(self):
        """String representation including timestamp and context."""
        context_str = f", context: {self.context}" if self.context else ""
        return f"[{self.timestamp}] {self.message}{context_str}"

class AmatakSyntaxError(AmatakError):
    """Syntax errors during parsing/lexing."""
    
    def __init__(self, message: str, line: int = None, column: int = None):
        """
        Initialize syntax error with location information.
        
        Args:
            message: Error description
            line: Line number where error occurred (default: None)
            column: Column number where error occurred (default: None)
        """
        context = {
            'line': line,
            'column': column,
            'error_type': 'syntax'
        }
        super().__init__(message, context)
        self.line = line
        self.column = column

class AmatakRuntimeError(AmatakError):
    """Errors during code execution."""
    
    def __init__(self, message: str, line: int = None, column: int = None):
        """
        Initialize runtime error with location information.
        
        Args:
            message: Error description
            line: Line number where error occurred (default: None)
            column: Column number where error occurred (default: None)
        """
        context = {
            'line': line,
            'column': column,
            'error_type': 'runtime'
        }
        super().__init__(message, context)
        self.line = line
        self.column = column

class CompilationError(AmatakError):
    """Errors during code compilation to bytecode or other targets."""
    pass

class SecurityError(AmatakError):
    """Security-related errors like sandbox violations or unsafe operations."""
    pass

class DatabaseError(AmatakError):
    """Database operation errors including connection and query failures."""
    pass

class TypeCheckError(AmatakError):
    """Type system validation errors during static analysis."""
    pass