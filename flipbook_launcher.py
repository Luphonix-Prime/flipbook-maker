import os
import sys
import webbrowser
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket

def get_resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

class FlipbookHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=get_resource_path('flipbook_data'), **kwargs)
    
    def log_message(self, format, *args):
        pass

def start_server(port):
    server = HTTPServer(('127.0.0.1', port), FlipbookHandler)
    print(f"Server started on http://127.0.0.1:{port}")
    server.serve_forever()

def main():
    port = find_free_port()
    
    server_thread = threading.Thread(target=start_server, args=(port,), daemon=True)
    server_thread.start()
    
    url = f'http://127.0.0.1:{port}/viewer.html'
    print(f"Opening flipbook at {url}")
    
    import time
    time.sleep(1)
    
    webbrowser.open(url)
    
    print("Flipbook is running. Close this window to exit.")
    print("Press Ctrl+C to stop the server.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")

if __name__ == '__main__':
    main()
