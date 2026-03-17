"""
Ingestion module for HR & Compliance RAG System
"""

from .loaders import load_text_files, load_all_documents
from .chunker import chunk_text, chunk_documents
from .validator import validate_document, validate_documents, filter_valid_documents
from .metadata_builder import (
    extract_metadata_from_document,
    build_metadata_for_source,
    build_metadata_csv,
    load_metadata
)

__all__ = [
    'load_text_files',
    'load_all_documents',
    'chunk_text',
    'chunk_documents',
    'validate_document',
    'validate_documents',
    'filter_valid_documents',
    'extract_metadata_from_document',
    'build_metadata_for_source',
    'build_metadata_csv',
    'load_metadata'
]
