"""
Metadata builder for HR & Compliance RAG System
Creates and manages document metadata
"""

import os
from typing import List, Dict
import pandas as pd


def extract_metadata_from_document(doc: Dict[str, str], source: str, doc_index: int) -> Dict[str, any]:
    """
    Extract metadata from a single document
    
    Args:
        doc: Document dictionary
        source: Source name (e.g., 'eur', 'pile_of_law')
        doc_index: Index of document in source
        
    Returns:
        Dictionary with metadata fields
    """
    text = doc.get('text', '')
    
    metadata = {
        'doc_id': f"{source}_{doc_index}",
        'source': source,
        'file_name': doc.get('file_name', ''),
        'file_path': doc.get('file_path', ''),
        'language': 'en',
        'document_type': 'legal',
        'text_length': len(text),
        'department': 'Legal',
        'category': 'Compliance',
        'region': 'Global'
    }
    
    return metadata


def build_metadata_for_source(documents: List[Dict[str, str]], source: str) -> List[Dict[str, any]]:
    """
    Build metadata for all documents from a source
    
    Args:
        documents: List of document dictionaries
        source: Source name
        
    Returns:
        List of metadata dictionaries
    """
    metadata_list = []
    
    for i, doc in enumerate(documents):
        metadata = extract_metadata_from_document(doc, source, i)
        metadata_list.append(metadata)
    
    return metadata_list


def build_metadata_csv(all_documents: Dict[str, List[Dict]], output_path: str = 'data/metadata.csv'):
    """
    Build metadata CSV from all documents
    
    Args:
        all_documents: Dictionary mapping source to documents
        output_path: Path to save metadata CSV
    """
    all_metadata = []
    
    for source, documents in all_documents.items():
        print(f"Building metadata for {source}...")
        metadata = build_metadata_for_source(documents, source)
        all_metadata.extend(metadata)
    
    # Create DataFrame
    df = pd.DataFrame(all_metadata)
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"Metadata saved to {output_path}")
    print(f"Total documents: {len(all_metadata)}")
    
    return df


def load_metadata(metadata_path: str = 'data/metadata.csv') -> pd.DataFrame:
    """
    Load metadata from CSV file
    
    Args:
        metadata_path: Path to metadata CSV
        
    Returns:
        DataFrame with metadata
    """
    if not os.path.exists(metadata_path):
        print(f"Metadata file not found: {metadata_path}")
        return pd.DataFrame()
    
    df = pd.read_csv(metadata_path)
    return df
