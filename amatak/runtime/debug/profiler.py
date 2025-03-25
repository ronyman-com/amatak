import time
import inspect
from collections import defaultdict
from typing import Dict, List, Tuple, Any, Callable
from ..errors import AmatakRuntimeError
from ..memory import memory_usage

class ExecutionProfile:
    """Stores profiling data for a single execution"""
    __slots__ = ['call_count', 'total_time', 'memory_usage', 'children']
    
    def __init__(self):
        self.call_count = 0
        self.total_time = 0.0
        self.memory_usage = []
        self.children = defaultdict(ExecutionProfile)

class Profiler:
    """Performance profiler for Amatak code execution"""
    
    def __init__(self):
        self._enabled = False
        self._call_stack = []
        self._profiles = defaultdict(ExecutionProfile)
        self._current_memory = None
        self._start_time = None
    
    def enable(self):
        """Enable profiling"""
        self._enabled = True
    
    def disable(self):
        """Disable profiling"""
        self._enabled = False
    
    def reset(self):
        """Reset all profiling data"""
        self._profiles.clear()
    
    def __enter__(self):
        self.enable()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disable()
    
    def profile_function(self, func: Callable) -> Callable:
        """Decorator to profile a function"""
        if not self._enabled:
            return func
        
        def wrapped(*args, **kwargs):
            with self:
                self.record_call(func.__name__)
                start = time.perf_counter()
                mem_before = memory_usage()
                
                try:
                    result = func(*args, **kwargs)
                finally:
                    mem_after = memory_usage()
                    duration = time.perf_counter() - start
                    self.record_return(func.__name__, duration, mem_after - mem_before)
                
                return result
        return wrapped
    
    def record_call(self, name: str):
        """Record a function call"""
        if not self._enabled:
            return
        
        if not self._call_stack:
            self._start_time = time.perf_counter()
        
        self._call_stack.append(name)
        self._current_memory = memory_usage()
        
        # Update profile for this call
        current = self._get_current_profile()
        current.call_count += 1
    
    def record_return(self, name: str, duration: float, mem_delta: float):
        """Record a function return"""
        if not self._enabled or not self._call_stack:
            return
        
        if self._call_stack[-1] != name:
            raise AmatakRuntimeError("Profiler call stack mismatch")
        
        current = self._get_current_profile()
        current.total_time += duration
        current.memory_usage.append(mem_delta)
        
        self._call_stack.pop()
    
    def _get_current_profile(self) -> ExecutionProfile:
        """Get profile for current call stack"""
        profile = self._profiles[self._call_stack[0]] if self._call_stack else None
        for name in self._call_stack[1:]:
            profile = profile.children[name]
        return profile
    
    def get_stats(self, min_time: float = 0.0) -> Dict[str, Dict]:
        """Get aggregated profiling statistics"""
        stats = {}
        
        for name, profile in self._profiles.items():
            self._aggregate_profile(stats, name, profile, min_time)
        
        total_time = time.perf_counter() - self._start_time if self._start_time else 0.0
        return {
            'functions': stats,
            'total_time': total_time,
            'call_count': sum(p.call_count for p in self._profiles.values())
        }
    
    def _aggregate_profile(self, stats: Dict, name: str, profile: ExecutionProfile, min_time: float):
        """Recursively aggregate profile data"""
        if profile.total_time < min_time:
            return
        
        avg_mem = sum(profile.memory_usage) / len(profile.memory_usage) if profile.memory_usage else 0
        
        stats[name] = {
            'call_count': profile.call_count,
            'total_time': profile.total_time,
            'avg_time': profile.total_time / profile.call_count,
            'avg_memory': avg_mem,
            'percent': (profile.total_time / (time.perf_counter() - self._start_time)) * 100 
                       if self._start_time else 0.0,
            'children': {}
        }
        
        for child_name, child_profile in profile.children.items():
            if child_profile.total_time >= min_time:
                self._aggregate_profile(
                    stats[name]['children'], 
                    child_name, 
                    child_profile, 
                    min_time
                )
    
    def print_report(self, min_time: float = 0.01, file=None):
        """Print formatted profiling report"""
        stats = self.get_stats(min_time)
        
        print("\n=== Execution Profile ===", file=file)
        print(f"Total time: {stats['total_time']:.4f}s", file=file)
        print(f"Total calls: {stats['call_count']}", file=file)
        print("\nFunction breakdown:", file=file)
        
        for name, data in stats['functions'].items():
            print(
                f"{name}: {data['call_count']} calls, "
                f"{data['total_time']:.4f}s total, "
                f"{data['avg_time']:.6f}s avg, "
                f"{data['percent']:.1f}%",
                file=file
            )
            
            if data['children']:
                print("  Children:", file=file)
                for child, child_data in data['children'].items():
                    print(
                        f"    {child}: {child_data['call_count']} calls, "
                        f"{child_data['total_time']:.4f}s total",
                        file=file
                    )