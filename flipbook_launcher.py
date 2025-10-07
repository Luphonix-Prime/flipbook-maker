import os
import sys
import webbrowser
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class FlipbookHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.directory = get_resource_path('flipbook_data')
        super().__init__(*args, directory=self.directory, **kwargs)
    
    def log_message(self, format, *args):
        # Suppress logging
        pass

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

def start_server(port):
    try:
        server = HTTPServer(('127.0.0.1', port), FlipbookHandler)
        print(f"Server started on http://127.0.0.1:{port}")
        server.serve_forever()
    except Exception as e:
        print(f"Server error: {e}")

def main():
    try:
        port = find_free_port()
        
        # Create server thread
        server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
        server_thread.start()
        
        # Wait for server to start
        time.sleep(1)
        
        # Open browser
        url = f'http://127.0.0.1:{port}/viewer.html'
        print(f"Opening flipbook at {url}")
        
        try:
            webbrowser.open(url)
        except Exception as e:
            print(f"Failed to open browser: {e}")
            print(f"Please open {url} manually in your browser")
        
        # Keep the application running
        while True:
            time.sleep(1)
            if not server_thread.is_alive():
                print("Server stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        raise  # Re-raise the exception for PyInstaller to handle
    finally:
        print("Exiting...")

if __name__ == '__main__':
    main()
