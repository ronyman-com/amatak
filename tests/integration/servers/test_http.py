import os
import unittest
import tempfile
import time
import requests
from threading import Thread
from amatak.servers import start_dev_server
from amatak.runtime import AMatakRuntime

class TestHTTPServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary directory with test files
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.test_port = 8888  # Use a different port than default
        
        # Create test Amatak files
        cls.hello_file = os.path.join(cls.temp_dir.name, "hello.amatak")
        with open(cls.hello_file, 'w') as f:
            f.write('print("Hello from Amatak!")')
        
        cls.math_file = os.path.join(cls.temp_dir.name, "math.amatak")
        with open(cls.math_file, 'w') as f:
            f.write('print(2 + 3 * 4)')
        
        # Start the server in a separate thread
        cls.server_thread = Thread(
            target=start_dev_server,
            kwargs={'root_path': cls.temp_dir.name, 'port': cls.test_port}
        )
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # Give the server time to start
        time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_hello_world(self):
        """Test basic Amatak script execution"""
        url = f"http://localhost:{self.test_port}/hello.amatak"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text.strip(), "Hello from Amatak!")

    def test_math_expression(self):
        """Test mathematical expression evaluation"""
        url = f"http://localhost:{self.test_port}/math.amatak"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text.strip(), "14")

    def test_nonexistent_file(self):
        """Test handling of non-existent files"""
        url = f"http://localhost:{self.test_port}/nonexistent.amatak"
        response = requests.get(url)
        self.assertEqual(response.status_code, 404)

    def test_static_files(self):
        """Test serving static files"""
        # Create a test static file
        static_file = os.path.join(self.temp_dir.name, "test.txt")
        with open(static_file, 'w') as f:
            f.write("Static file content")
        
        url = f"http://localhost:{self.test_port}/test.txt"
        response = requests.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text.strip(), "Static file content")

    def test_invalid_amatak(self):
        """Test handling of invalid Amatak code"""
        invalid_file = os.path.join(self.temp_dir.name, "invalid.amatak")
        with open(invalid_file, 'w') as f:
            f.write('print("Unclosed string)')
        
        url = f"http://localhost:{self.test_port}/invalid.amatak"
        response = requests.get(url)
        self.assertEqual(response.status_code, 500)
        self.assertIn("Error", response.text)

class TestHTTPIntegration(unittest.TestCase):
    def setUp(self):
        self.runtime = AMatakRuntime()
        self.test_port = 8889
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a simple web handler file
        self.web_file = os.path.join(self.temp_dir.name, "web.amatak")
        with open(self.web_file, 'w') as f:
            f.write("""
            if path == '/hello':
                print("<h1>Hello Web!</h1>")
            else:
                print("<h1>Not Found</h1>")
            """)
        
        # Start server
        self.server_thread = Thread(
            target=start_dev_server,
            kwargs={
                'root_path': self.temp_dir.name,
                'port': self.test_port
            }
        )
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(0.5)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_web_handler(self):
        """Test web route handling"""
        response = requests.get(f"http://localhost:{self.test_port}/web.amatak?path=/hello")
        self.assertEqual(response.status_code, 200)
        self.assertIn("<h1>Hello Web!</h1>", response.text)
        
        response = requests.get(f"http://localhost:{self.test_port}/web.amatak?path=/other")
        self.assertEqual(response.status_code, 200)
        self.assertIn("<h1>Not Found</h1>", response.text)

if __name__ == '__main__':
    unittest.main()