import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from amatak.runtime import AMatakRuntime

class AmatakHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, runtime, *args, **kwargs):
        self.runtime = runtime
        super().__init__(*args, **kwargs)

    def do_GET(self):
        try:
            parsed_path = urlparse(self.path)
            file_path = parsed_path.path.lstrip('/')
            query_params = parse_qs(parsed_path.query)
            
            # Check if requesting an Amatak file
            if file_path.endswith('.amatak'):
                self.handle_amatak_file(file_path, query_params)
            else:
                self.handle_static_file(file_path)
        except Exception as e:
            self.send_error(500, f"Server Error: {str(e)}")

    def handle_amatak_file(self, file_path, query_params):
        full_path = os.path.join(os.getcwd(), file_path)
        
        if not os.path.exists(full_path):
            self.send_error(404, "File Not Found")
            return
        
        with open(full_path, 'r') as f:
            source = f.read()
        
        # Create a new scope with query parameters
        scope = {}
        for key, values in query_params.items():
            scope[key] = values[0] if len(values) == 1 else values
        
        # Execute the script
        try:
            result = self.runtime.execute(source, scope)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(str(result).encode('utf-8'))
        except Exception as e:
            self.send_error(500, f"Execution Error: {str(e)}")

    def handle_static_file(self, file_path):
        full_path = os.path.join(os.getcwd(), file_path)
        
        if not os.path.exists(full_path):
            self.send_error(404, "File Not Found")
            return
        
        # Determine content type
        content_type = 'text/plain'
        if file_path.endswith('.html'):
            content_type = 'text/html'
        elif file_path.endswith('.css'):
            content_type = 'text/css'
        elif file_path.endswith('.js'):
            content_type = 'application/javascript'
        
        with open(full_path, 'rb') as f:
            content = f.read()
        
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(content)

def start_dev_server(root_path='.', port=8000, host='localhost'):
    """Start the development HTTP server"""
    os.chdir(root_path)
    runtime = AMatakRuntime()
    
    def handler(*args, **kwargs):
        return AmatakHTTPRequestHandler(runtime, *args, **kwargs)
    
    server = HTTPServer((host, port), handler)
    print(f"Server started at http://{host}:{port}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
        server.shutdown()