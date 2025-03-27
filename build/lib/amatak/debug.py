import inspect
import time
from functools import wraps
from typing import Callable, Any
from ..error_handling import error_handler

class DebugTools:
    """Debugging utilities for development"""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.metrics = {}
        
    def trace(self, func: Callable) -> Callable:
        """Decorator to trace function execution"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.enabled:
                return func(*args, **kwargs)
                
            start_time = time.time()
            frame = inspect.currentframe()
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                call_stack = inspect.getouterframes(frame)
                call_info = {
                    'function': func.__name__,
                    'args': args,
                    'kwargs': kwargs,
                    'return': result,
                    'time': elapsed,
                    'caller': call_stack[1].function if len(call_stack) > 1 else None
                }
                
                self._record_metric(func.__name__, elapsed)
                error_handler.logger.debug(f"TRACE: {call_info}")
                return result
            except Exception as e:
                error_handler.log_error(e, {
                    'trace': True,
                    'function': func.__name__
                })
                raise
            finally:
                del frame
        return wrapper
    
    def _record_metric(self, name: str, value: float):
        """Record performance metrics"""
        if name not in self.metrics:
            self.metrics[name] = {
                'count': 0,
                'total': 0,
                'max': 0,
                'min': float('inf')
            }
            
        self.metrics[name]['count'] += 1
        self.metrics[name]['total'] += value
        self.metrics[name]['max'] = max(self.metrics[name]['max'], value)
        self.metrics[name]['min'] = min(self.metrics[name]['min'], value)
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            name: {
                **stats,
                'avg': stats['total'] / stats['count'] if stats['count'] else 0
            }
            for name, stats in self.metrics.items()
        }

# Global debug tools instance
debug_tools = DebugTools()