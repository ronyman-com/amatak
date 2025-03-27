import json
from typing import Any, Dict, Callable
from concurrent.futures import ThreadPoolExecutor
from ....errors import AmatakRuntimeError
from ....runtime.types.core import FunctionType

class RPCServer:
    """JSON-RPC 2.0 compliant server implementation"""
    
    def __init__(self, max_workers: int = 10):
        self.methods: Dict[str, Callable] = {}
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.middlewares = []
    
    def register_method(self, name: str, func: Callable):
        """Register an RPC method"""
        if not callable(func):
            raise AmatakRuntimeError(f"RPC method {name} must be callable")
        self.methods[name] = func
    
    def register_object(self, obj: Any, prefix: str = ""):
        """Register all public methods of an object"""
        for name in dir(obj):
            if not name.startswith('_'):
                attr = getattr(obj, name)
                if callable(attr):
                    self.register_method(f"{prefix}{name}", attr)
    
    def add_middleware(self, middleware: Callable):
        """Add middleware for request processing"""
        self.middlewares.append(middleware)
    
    async def handle_request(self, request: str) -> str:
        """Process a JSON-RPC request"""
        try:
            # Parse request
            try:
                data = json.loads(request)
            except json.JSONDecodeError:
                return self._error_response(None, -32700, "Parse error")
            
            # Handle batch requests
            if isinstance(data, list):
                results = await asyncio.gather(*[self._process_single(req) for req in data])
                return json.dumps([r for r in results if r is not None])
            
            # Single request
            return await self._process_single(data)
        except Exception as e:
            return self._error_response(None, -32603, f"Internal error: {str(e)}")
    
    async def _process_single(self, data: Dict) -> str:
        """Process a single RPC request"""
        # Validate request
        if not isinstance(data, dict):
            return self._error_response(None, -32600, "Invalid Request")
        
        try:
            method = data['method']
            params = data.get('params', [])
            request_id = data.get('id')
        except KeyError:
            return self._error_response(None, -32600, "Invalid Request")
        
        # Apply middlewares
        for middleware in self.middlewares:
            method, params = await middleware(method, params)
        
        # Execute method
        if method not in self.methods:
            return self._error_response(request_id, -32601, "Method not found")
        
        try:
            if isinstance(params, dict):
                result = await self.executor.submit(self.methods[method], **params)
            else:
                result = await self.executor.submit(self.methods[method], *params)
            
            return self._success_response(request_id, result)
        except Exception as e:
            return self._error_response(request_id, -32603, f"Method execution error: {str(e)}")
    
    def _success_response(self, request_id: Any, result: Any) -> str:
        """Create success response"""
        return json.dumps({
            "jsonrpc": "2.0",
            "result": result,
            "id": request_id
        })
    
    def _error_response(self, request_id: Any, code: int, message: str) -> str:
        """Create error response"""
        return json.dumps({
            "jsonrpc": "2.0",
            "error": {
                "code": code,
                "message": message
            },
            "id": request_id
        })
    
    async def start(self, host: str = "0.0.0.0", port: int = 8080):
        """Start the RPC server (implement in transport-specific subclass)"""
        raise NotImplementedError("Use HTTPRPCServer or WebSocketRPCServer")

class HTTPRPCServer(RPCServer):
    """HTTP transport for RPC server"""
    
    async def start(self, host: str = "0.0.0.0", port: int = 8080):
        """Start HTTP RPC server"""
        from aiohttp import web
        
        app = web.Application()
        app.add_routes([web.post('/', self._http_handler)])
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        print(f"HTTP RPC server running on http://{host}:{port}")
    
    async def _http_handler(self, request):
        """Handle HTTP requests"""
        data = await request.text()
        response = await self.handle_request(data)
        return web.json_response(json.loads(response))