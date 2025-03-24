class AmatakError(Exception):
    """Base class for all Amatak exceptions"""
    pass

class AmatakSyntaxError(AmatakError):
    """Syntax error in Amatak code"""
    def __init__(self, message, line=None, column=None):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"SyntaxError: {message} at line {line}, column {column}")

class AmatakRuntimeError(AmatakError):
    """Runtime error during execution"""
    def __init__(self, message, line=None):
        self.message = message
        self.line = line
        super().__init__(f"RuntimeError: {message} at line {line}")