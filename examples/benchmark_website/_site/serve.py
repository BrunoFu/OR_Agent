#!/usr/bin/env python3
"""
Simple HTTP server to serve the benchmark website.
Run this script from anywhere - it will automatically serve from the correct directory.
"""
import http.server
import socketserver
import os
from pathlib import Path

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).resolve().parent
os.chdir(SCRIPT_DIR)

PORT = 8000

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SCRIPT_DIR), **kwargs)

def main():
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Server running at http://127.0.0.1:{PORT}/")
        print(f"Serving directory: {SCRIPT_DIR}")
        print(f"Open in browser: http://127.0.0.1:{PORT}/index.html")
        print("Press Ctrl+C to stop the server")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()
