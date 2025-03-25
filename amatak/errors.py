from datetime import datetime

class AmatakError(Exception):
    """Base class for all Amatak errors"""
    def __init__(self, message: str, context: dict = None):
        super().__init__(message)
        self.context = context or {}
        self.timestamp = datetime.utcnow().isoformat()

class AmatakSyntaxError(AmatakError):
    """Syntax errors during parsing/lexing"""
    def __init__(self, message: str, line: int = None, column: int = None):
        super().__init__(message)
        self.line = line
        self.column = column
        self.context = {
            'line': line,
            'column': column
        }

class AmatakRuntimeError(AmatakError):
    """Errors during code execution"""
    def __init__(self, message: str, line: int = None, column: int = None):
        super().__init__(message)
        self.line = line
        self.column = column
        self.context = {
            'line': line,
            'column': column
        }

class CompilationError(AmatakError):
    """Errors during code compilation"""
    pass

class SecurityError(AmatakError):
    """Security-related errors"""
    pass

class DatabaseError(AmatakError):
    """Database operation errors"""
    pass

class TypeCheckError(AmatakError):
    """Type system validation errors"""
    pass