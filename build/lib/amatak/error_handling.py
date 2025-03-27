import logging
import traceback
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

class ErrorHandler:
    """Centralized error handling and logging system"""
    
    def __init__(self, log_dir: str = "logs", debug: bool = False):
        self.log_dir = Path(log_dir)
        self.debug = debug
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging system"""
        self.log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.DEBUG if self.debug else logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_dir / 'amatak.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('amatak')

    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log an error with context"""
        exc_info = traceback.format_exc()
        error_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "error_type": type(error).__name__,
            "message": str(error),
            "traceback": exc_info,
            "context": context or {}
        }
        
        self.logger.error(f"Error occurred: {error_data}")
        
        # Write to error-specific log file
        error_log = self.log_dir / 'errors.log'
        with open(error_log, 'a') as f:
            f.write(f"{error_data}\n")

    def wrap_operation(self, operation, *args, **kwargs):
        """Decorator to wrap operations with error handling"""
        try:
            return operation(*args, **kwargs)
        except Exception as e:
            self.log_error(e, {
                "operation": operation.__name__,
                "args": args,
                "kwargs": kwargs
            })
            if self.debug:
                raise
            return None

# Global error handler instance
error_handler = ErrorHandler()