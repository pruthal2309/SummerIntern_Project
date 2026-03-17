"""
Document loaders for HR & Compliance RAG System
Loads documents from the raw data directory
"""

import os
from typing import List, Dict


def load_text_files(directory: str) -> List[Dict[str, str]]:
    """
    Load all text files from a directory
    
    Args:
        directory: Path to directory containing text files
        
    Returns:
        List of dictionaries with file_path and text content
    """
    documents = []
    
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return documents
    
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):
            file_path = os.path.join(directory, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    documents.append({
                        'file_path': file_path,
                        'file_name': filename,
                        'text': text
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return documents


def load_all_documents(base_dir: str = 'data/raw') -> Dict[str, List[Dict]]:
    """
    Load documents from all subdirectories
    
    Args:
        base_dir: Base directory containing document folders
        
    Returns:
        Dictionary mapping source name to list of documents
    """
    all_documents = {}
    
    if not os.path.exists(base_dir):
        print(f"Base directory not found: {base_dir}")
        return all_documents
    
    # Get all subdirectories
    for source_name in os.listdir(base_dir):
        source_path = os.path.join(base_dir, source_name)
        
        if os.path.isdir(source_path):
            print(f"Loading documents from: {source_name}")
            documents = load_text_files(source_path)
            all_documents[source_name] = documents
            print(f"  Loaded {len(documents)} documents")
    
    return all_documents
