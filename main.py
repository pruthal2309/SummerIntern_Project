"""
Main Entry Point for HR & Compliance RAG System
Redirects to backend/main.py for all operations
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import and run backend main
from backend.main import main

if __name__ == "__main__":
    main()
