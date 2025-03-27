from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import webbrowser
from ..runtime import AMatakRuntime

class DevHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, runtime=None, **kwargs):
        self.runtime = runtime
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path.endswith('.ak'):
            self._handle_amatak_request()
        else:
            super().do_GET()

    def _handle_amatak_request(self):
        try:
            with open(self.path[1:], 'r') as f:
                source = f.read()
            
            # Execute the Amatak code
            result = self.runtime.interpreter.execute(source)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(str(result).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Error: {str(e)}".encode())

def start_dev_server(root_path='.', port=8000):
    """Start development server with Amatak support"""
    runtime = AMatakRuntime()
    
    def handler(*args, **kwargs):
        return DevHTTPRequestHandler(*args, runtime=runtime, **kwargs)
    
    os.chdir(root_path)
    server = HTTPServer(('localhost', port), handler)
    
    url = f"http://localhost:{port}"
    print(f"Serving at {url}")
    print("Press Ctrl+C to stop")
    
    # Open browser automatically
    webbrowser.open(url)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()