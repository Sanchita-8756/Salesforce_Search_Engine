#!/usr/bin/env python3
"""
Simple startup script to run the Salesforce MCP application.
Starts both the FastAPI backend and serves the frontend.
"""

import os
import sys
import subprocess
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser

def start_backend():
    """Start the FastAPI backend server."""
    print("Starting FastAPI backend...")
    os.chdir(os.path.join(os.path.dirname(__file__), "backend"))
    subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"])

def start_frontend():
    """Start a simple HTTP server for the frontend."""
    print("Starting frontend server...")
    os.chdir(os.path.join(os.path.dirname(__file__), "frontend"))
    
    class CORSRequestHandler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            super().end_headers()
        
        def do_OPTIONS(self):
            self.send_response(200)
            self.end_headers()
    
    server = HTTPServer(('localhost', 3000), CORSRequestHandler)
    print("Frontend server running at http://localhost:3000")
    server.serve_forever()

if __name__ == "__main__":
    print("Starting Salesforce MCP Application...")
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(3)
    
    # Start frontend in a separate thread
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    frontend_thread.start()
    
    # Give frontend time to start
    time.sleep(2)
    
    # Open browser
    print("Opening browser...")
    webbrowser.open("http://localhost:3000")
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)