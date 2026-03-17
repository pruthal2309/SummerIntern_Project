#!/usr/bin/env python3
"""
Start the complete RAG system with API and Frontend
"""

import os
import sys
import time
import subprocess
import threading
import webbrowser
from pathlib import Path

# Ensure we always run from repository root (so relative paths work)
REPO_ROOT = Path(__file__).resolve().parents[1]
os.chdir(REPO_ROOT)

def check_system_ready():
    """Check if the system is ready"""
    print("🔍 Checking system readiness...")
    
    required_files = [
        "data/processed/faiss_index.bin",
        "data/processed/index_metadata.json",
        "data/processed/embeddings.npy"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ Missing: {file_path}")
            return False
    
    print("✅ System files ready")
    return True

def start_api_server():
    """Start the RAG API server"""
    print("🚀 Starting RAG API Server...")
    
    try:
        # Use the backend package entrypoint to avoid depending on a top-level script.
        process = subprocess.Popen([
            sys.executable, "-m", "backend.main", "--serve"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        print("⏳ Waiting for API server to initialize...")
        time.sleep(10)
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def start_frontend_server():
    """Start the frontend server"""
    print("🌐 Starting Frontend Server...")
    
    try:
        frontend_dir = Path("frontend")
        
        process = subprocess.Popen([
            sys.executable, "-m", "http.server", "3000"
        ], cwd=frontend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        time.sleep(2)
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start frontend server: {e}")
        return None

def open_browser():
    """Open the browser after a delay"""
    time.sleep(3)
    try:
        webbrowser.open('http://localhost:3000')
        print("🌐 Browser opened to http://localhost:3000")
    except:
        print("⚠️  Could not open browser automatically")

def main():
    """Main function to start the complete system"""
    print("🚀 HR & Compliance RAG System - Full Startup")
    print("=" * 60)
    
    # Check if system is ready
    if not check_system_ready():
        print("\n⚠️  System not ready. Please run the pipeline first:")
        print("   python -m backend.main --pipeline")
        return
    
    print("\n📋 Starting complete system...")
    print("   - API Server: http://localhost:8000")
    print("   - Frontend: http://localhost:3000")
    print("   - API Docs: http://localhost:8000/docs")
    
    # Start API server
    api_process = start_api_server()
    if not api_process:
        print("❌ Failed to start API server")
        return
    
    # Start frontend server
    frontend_process = start_frontend_server()
    if not frontend_process:
        print("❌ Failed to start frontend server")
        api_process.terminate()
        return
    
    # Open browser in a separate thread
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    print("\n✅ System started successfully!")
    print("\n🎯 Access Points:")
    print("   - Web Interface: http://localhost:3000")
    print("   - API Documentation: http://localhost:8000/docs")
    print("   - Health Check: http://localhost:8000/health")
    
    print(f"\n⏹️  Press Ctrl+C to stop both servers")
    
    try:
        while True:
            time.sleep(1)
            
            if api_process.poll() is not None:
                print("❌ API server stopped unexpectedly")
                break
                
            if frontend_process.poll() is not None:
                print("❌ Frontend server stopped unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        
        if api_process:
            api_process.terminate()
            print("   ✅ API server stopped")
            
        if frontend_process:
            frontend_process.terminate()
            print("   ✅ Frontend server stopped")
        
        print("👋 System shutdown complete")

if __name__ == "__main__":
    main()
