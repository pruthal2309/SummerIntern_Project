"""
Data validation utilities for HR & Compliance RAG System
Validates document quality and content
"""

from typing import List, Dict


def validate_document(doc: Dict[str, str]) -> bool:
    """
    Validate a single document
    
    Args:
        doc: Document dictionary
        
    Returns:
        True if document is valid, False otherwise
    """
    # Check if text field exists
    if 'text' not in doc:
        return False
    
    text = doc['text']
    
    # Check if text is not empty
    if not text or len(text.strip()) == 0:
        return False
    
    # Check minimum length (at least 10 characters)
    if len(text) < 10:
        return False
    
    return True


def validate_documents(documents: List[Dict[str, str]]) -> Dict[str, any]:
    """
    Validate multiple documents and return statistics
    
    Args:
        documents: List of document dictionaries
        
    Returns:
        Dictionary with validation statistics
    """
    total = len(documents)
    valid = 0
    invalid = 0
    empty = 0
    too_short = 0
    
    for doc in documents:
        if validate_document(doc):
            valid += 1
        else:
            invalid += 1
            text = doc.get('text', '')
            if not text or len(text.strip()) == 0:
                empty += 1
            elif len(text) < 10:
                too_short += 1
    
    return {
        'total': total,
        'valid': valid,
        'invalid': invalid,
        'empty': empty,
        'too_short': too_short,
        'valid_percentage': (valid / total * 100) if total > 0 else 0
    }


def filter_valid_documents(documents: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Filter out invalid documents
    
    Args:
        documents: List of document dictionaries
        
    Returns:
        List of valid documents only
    """
    return [doc for doc in documents if validate_document(doc)]
