"""
Vector store module for HR & Compliance RAG System
"""

from .embedding_generator import (
    load_embedding_model,
    generate_embeddings,
    generate_embeddings_from_sources,
    save_embeddings,
    load_embeddings,
    validate_embeddings
)

from .build_index import (
    load_chunks_from_week1,
    build_faiss_index,
    save_faiss_index,
    load_faiss_index
)

__all__ = [
    'load_embedding_model',
    'generate_embeddings', 
    'generate_embeddings_from_sources',
    'save_embeddings',
    'load_embeddings',
    'validate_embeddings',
    'load_chunks_from_week1',
    'build_faiss_index',
    'save_faiss_index',
    'load_faiss_index'
]