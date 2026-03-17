"""
Configuration management for HR & Compliance RAG System
Centralizes all configuration settings
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Central configuration class"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    BACKEND_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    METADATA_FILE = DATA_DIR / "metadata.csv"
    
    # API Settings
    API_HOST = os.getenv("API_HOST", "localhost")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # Embedding Settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_DIMENSION = int(os.getenv("EMBEDDING_DIMENSION", 384))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", 32))
    
    # FAISS Index Settings
    FAISS_INDEX_TYPE = os.getenv("FAISS_INDEX_TYPE", "flat")
    FAISS_INDEX_PATH = PROCESSED_DATA_DIR / "faiss_index.bin"
    INDEX_METADATA_PATH = PROCESSED_DATA_DIR / "index_metadata.json"
    EMBEDDINGS_PATH = PROCESSED_DATA_DIR / "embeddings.npy"
    CHUNKS_METADATA_PATH = PROCESSED_DATA_DIR / "chunks_metadata.json"
    
    # LLM Settings (Groq)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL_NAME = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", 1024))
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.1))
    
    # RAG Settings
    RAG_TOP_K = int(os.getenv("RAG_TOP_K", 5))
    
    # Document Processing Settings
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 200))
    MIN_DOC_LENGTH = int(os.getenv("MIN_DOC_LENGTH", 10))
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        # Check required directories
        if not cls.DATA_DIR.exists():
            errors.append(f"Data directory not found: {cls.DATA_DIR}")
        
        # Check API key
        if not cls.GROQ_API_KEY or cls.GROQ_API_KEY == "your_groq_api_key_here":
            errors.append("GROQ_API_KEY not set in .env file")
        
        return errors
    
    @classmethod
    def get_summary(cls):
        """Get configuration summary"""
        return {
            "api": {
                "host": cls.API_HOST,
                "port": cls.API_PORT
            },
            "embedding": {
                "model": cls.EMBEDDING_MODEL,
                "dimension": cls.EMBEDDING_DIMENSION,
                "batch_size": cls.BATCH_SIZE
            },
            "llm": {
                "model": cls.GROQ_MODEL_NAME,
                "max_tokens": cls.LLM_MAX_TOKENS,
                "temperature": cls.LLM_TEMPERATURE
            },
            "rag": {
                "top_k": cls.RAG_TOP_K
            },
            "processing": {
                "chunk_size": cls.CHUNK_SIZE,
                "chunk_overlap": cls.CHUNK_OVERLAP
            }
        }


# Create config instance
config = Config()
