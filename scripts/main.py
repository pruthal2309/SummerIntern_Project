"""
Main Entry Point for HR & Compliance RAG System
Redirects to backend/main.py for all operations
"""

import sys
import os
from pathlib import Path

# Ensure we always run from repository root (so relative paths work)
REPO_ROOT = Path(__file__).resolve().parents[1]
os.chdir(REPO_ROOT)

# Add repository root to path for imports
sys.path.insert(0, str(REPO_ROOT))

# Import and run backend main
from backend.main import main

if __name__ == "__main__":
    main()
