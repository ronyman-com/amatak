"""
DateTime compatibility layer
"""

import time
from datetime import datetime, timedelta
from typing import Optional, Union

class DateTimeCompat:
    """Cross-platform datetime operations"""
    
    @staticmethod
    def now() -> datetime:
        """Current time with microseconds"""
        return datetime.now()
    
    @staticmethod
    def utcnow() -> datetime:
        """UTC timestamp"""
        return datetime.utcnow()
    
    @staticmethod
    def strftime(dt: datetime, fmt: str) -> str:
        """Safe string formatting"""
        try:
            return dt.strftime(fmt)
        except ValueError as e:
            raise ValueError(f"Invalid format: {str(e)}")
    
    @staticmethod
    def sleep(seconds: Union[int, float]) -> None:
        """Precision sleep"""
        time.sleep(seconds)

# Public API
datetime = DateTimeCompat()