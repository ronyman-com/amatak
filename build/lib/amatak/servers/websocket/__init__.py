import asyncio
import json
from typing import Dict, Any, Callable
from aiohttp import web, WSMsgType
from ....errors import AmatakRuntimeError
from ....runtime.types.core import FunctionType

class WebSocketRuntime:
    """WebSocket server for real-time communication"""
    
    def __init__(self, max_connections: int = 100):
        self.connections = set()
        self.message_handlers = {}
        self.event_handlers = {}
        self.middlewares = []
    
    def on_message(self, message_type: str):
        """Decorator to register message handlers"""
        def decorator(handler):
            self.message_handlers[message_type] = handler
            return handler
        return decorator
    
    def on_event(self, event: str):
        """Decorator to register event handlers"""
        def decorator(handler):
            self.event_handlers[event] = handler
            return handler
        return decorator
    
    def add_middleware(self, middleware: Callable):
        """Add middleware for message processing"""
        self.middlewares.append(middleware)
    
    async def broadcast(self, message: Dict):
        """Broadcast message to all connected clients"""
        message_json = json.dumps(message)
        for ws in self.connections.copy():
            try:
                await ws.send_str(message_json)
            except ConnectionError:
                self.connections.remove(ws)
    
    async def start(self, host: str = "0.0.0.0", port: int = 8081):
        """Start WebSocket server"""
        app = web.Application()
        app.add_routes([web.get('/', self._websocket_handler)])
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        print(f"WebSocket server running on ws://{host}:{port}")
    
    async def _websocket_handler(self, request):
        """Handle WebSocket connections"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.connections.add(ws)
        
        try:
            # Call connect handler if exists
            if 'connect' in self.event_handlers:
                await self.event_handlers['connect'](ws)
            
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        await self._process_message(ws, data)
                    except json.JSONDecodeError:
                        await ws.send_str(json.dumps({
                            'error': 'Invalid JSON format'
                        }))
                elif msg.type == WSMsgType.ERROR:
                    print(f"WebSocket error: {ws.exception()}")
        
        finally:
            self.connections.discard(ws)
            # Call disconnect handler if exists
            if 'disconnect' in self.event_handlers:
                await self.event_handlers['disconnect'](ws)
            
            await ws.close()
        
        return ws
    
    async def _process_message(self, ws, message: Dict):
        """Process incoming WebSocket message"""
        if not isinstance(message, dict) or 'type' not in message:
            await ws.send_str(json.dumps({
                'error': 'Invalid message format'
            }))
            return
        
        message_type = message['type']
        payload = message.get('data', {})
        
        # Apply middlewares
        for middleware in self.middlewares:
            message_type, payload = await middleware(message_type, payload)
        
        # Find handler
        if message_type in self.message_handlers:
            try:
                response = await self.message_handlers[message_type](ws, payload)
                if response is not None:
                    await ws.send_str(json.dumps({
                        'type': f"{message_type}_response",
                        'data': response
                    }))
            except Exception as e:
                await ws.send_str(json.dumps({
                    'type': 'error',
                    'data': {
                        'message': str(e),
                        'original_type': message_type
                    }
                }))
        else:
            await ws.send_str(json.dumps({
                'type': 'error',
                'data': {
                    'message': f"No handler for message type '{message_type}'"
                }
            }))

class WebSocketRPCServer(RPCServer):
    """RPC over WebSocket implementation"""
    
    async def start(self, host: str = "0.0.0.0", port: int = 8081):
        """Start WebSocket RPC server"""
        self.ws_runtime = WebSocketRuntime()
        
        @self.ws_runtime.on_message('rpc')
        async def handle_rpc(ws, payload):
            response = await self.handle_request(json.dumps(payload))
            return json.loads(response)
        
        await self.ws_runtime.start(host, port)