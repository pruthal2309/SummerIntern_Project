"""
Text chunking utilities for HR & Compliance RAG System
Splits documents into smaller chunks for embedding
"""

from typing import List, Dict


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum size of each chunk in characters
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text or len(text) == 0:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        if chunk.strip():
            chunks.append(chunk)
        
        start += (chunk_size - overlap)
    
    return chunks


def chunk_documents(documents: List[Dict[str, str]], 
                    chunk_size: int = 1000, 
                    overlap: int = 200) -> List[Dict[str, any]]:
    """
    Chunk multiple documents and preserve metadata
    
    Args:
        documents: List of document dictionaries with 'text' field
        chunk_size: Maximum size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of chunk dictionaries with metadata
    """
    all_chunks = []
    
    for doc in documents:
        text = doc.get('text', '')
        chunks = chunk_text(text, chunk_size, overlap)
        
        for i, chunk in enumerate(chunks):
            chunk_dict = {
                'text': chunk,
                'chunk_id': i,
                'file_name': doc.get('file_name', ''),
                'file_path': doc.get('file_path', ''),
                'total_chunks': len(chunks)
            }
            all_chunks.append(chunk_dict)
    
    return all_chunks
