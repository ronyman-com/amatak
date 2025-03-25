import sys
import inspect
from typing import List, Dict, Any, Optional
from ..errors import AmatakRuntimeError

class ExecutionTrace:
    """Represents a single execution trace event"""
    __slots__ = ['event_type', 'name', 'timestamp', 'data', 'depth']
    
    def __init__(self, event_type: str, name: str, depth: int, data: Any = None):
        self.event_type = event_type  # 'call', 'return', 'line', 'exception'
        self.name = name
        self.timestamp = time.perf_counter()
        self.data = data
        self.depth = depth
    
    def __repr__(self):
        return f"{'  '*self.depth}{self.event_type} {self.name} ({self.timestamp:.6f})"

class Tracer:
    """Execution tracer for debugging and analysis"""
    
    def __init__(self):
        self._enabled = False
        self._traces: List[ExecutionTrace] = []
        self._call_stack = []
        self._depth = 0
        self._last_line = None
        self._filters = []
    
    def enable(self):
        """Enable tracing"""
        self._enabled = True
        sys.settrace(self._trace_function)
    
    def disable(self):
        """Disable tracing"""
        self._enabled = False
        sys.settrace(None)
    
    def reset(self):
        """Clear all traces"""
        self._traces.clear()
        self._call_stack.clear()
        self._depth = 0
    
    def __enter__(self):
        self.enable()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disable()
    
    def add_filter(self, filter_func: Callable[[ExecutionTrace], bool]):
        """Add a trace filter function"""
        self._filters.append(filter_func)
    
    def _should_trace(self, trace: ExecutionTrace) -> bool:
        """Check if trace should be recorded"""
        return all(f(trace) for f in self._filters)
    
    def _trace_function(self, frame, event: str, arg):
        """Python trace function implementation"""
        if not self._enabled:
            return None
        
        code = frame.f_code
        filename = code.co_filename
        lineno = frame.f_lineno
        name = code.co_name
        
        # Skip internal files
        if filename.startswith('<') or 'site-packages' in filename:
            return None
        
        if event == 'call':
            self._depth += 1
            trace = ExecutionTrace('call', name, self._depth, {
                'file': filename,
                'line': lineno,
                'locals': frame.f_locals
            })
            self._call_stack.append((name, time.perf_counter()))
        
        elif event == 'return':
            trace = ExecutionTrace('return', name, self._depth, {
                'return': arg,
                'time': time.perf_counter() - self._call_stack[-1][1]
            })
            self._depth -= 1
            self._call_stack.pop()
        
        elif event == 'line':
            if self._last_line == lineno:
                return self._trace_function
            self._last_line = lineno
            trace = ExecutionTrace('line', name, self._depth, {
                'file': filename,
                'line': lineno,
                'locals': frame.f_locals
            })
        
        elif event == 'exception':
            trace = ExecutionTrace('exception', name, self._depth, {
                'exception': arg[1],
                'file': filename,
                'line': lineno
            })
        else:
            return self._trace_function
        
        if self._should_trace(trace):
            self._traces.append(trace)
        
        return self._trace_function
    
    def get_traces(self, filter_types: Optional[List[str]] = None) -> List[ExecutionTrace]:
        """Get filtered traces"""
        if filter_types:
            return [t for t in self._traces if t.event_type in filter_types]
        return self._traces.copy()
    
    def print_trace(self, filter_types: Optional[List[str]] = None, file=None):
        """Print execution trace"""
        traces = self.get_traces(filter_types)
        
        print("\n=== Execution Trace ===", file=file)
        for trace in traces:
            print(trace, file=file)
    
    def get_call_graph(self) -> Dict:
        """Generate call graph from traces"""
        graph = {}
        stack = []
        
        for trace in self._traces:
            if trace.event_type == 'call':
                node = {
                    'name': trace.name,
                    'time': trace.timestamp,
                    'children': [],
                    'data': trace.data
                }
                
                if stack:
                    stack[-1]['children'].append(node)
                else:
                    graph[trace.name] = node
                
                stack.append(node)
            
            elif trace.event_type == 'return' and stack:
                node = stack.pop()
                node['duration'] = trace.timestamp - node['time']
                node['return'] = trace.data
        
        return graph
    
    def find_bottlenecks(self, min_time: float = 0.1) -> List[Dict]:
        """Identify performance bottlenecks"""
        graph = self.get_call_graph()
        bottlenecks = []
        
        def _analyze(node):
            if node.get('duration', 0) >= min_time:
                bottlenecks.append({
                    'function': node['name'],
                    'duration': node['duration'],
                    'location': node['data'].get('file', 'unknown'),
                    'line': node['data'].get('line', 0)
                })
            
            for child in node.get('children', []):
                _analyze(child)
        
        for root in graph.values():
            _analyze(root)
        
        return sorted(bottlenecks, key=lambda x: x['duration'], reverse=True)