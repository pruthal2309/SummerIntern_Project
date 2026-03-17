"""
FAISS Vector Database Builder for HR & Compliance RAG System
Builds searchable vector index from embeddings
"""

import os
import json
import numpy as np
import faiss
from typing import List, Dict, Tuple, Optional
import pandas as pd

from backend.vectorstore.embedding_generator import (
    load_embedding_model,
    generate_embeddings_from_sources,
    save_embeddings,
    validate_embeddings
)


def load_chunks_from_week1() -> Dict[str, List[Dict]]:
    """
    Load chunks from Week 1 pipeline output
    Converts to format needed for embedding generation
    """
    print("Loading chunks from Week 1 pipeline...")
    
    # Load metadata
    metadata_path = "data/metadata.csv"
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
    
    try:
        metadata_df = pd.read_csv(metadata_path)
        print(f"Loaded metadata with {len(metadata_df)} entries")
    except Exception as e:
        raise Exception(f"Failed to load metadata CSV: {e}")
    
    # Group by source and load corresponding text files
    chunks_by_source = {}
    
    for source in metadata_df['source'].unique():
        print(f"Loading chunks for source: {source}")
        source_docs = metadata_df[metadata_df['source'] == source]
        
        chunks = []
        loaded_count = 0
        error_count = 0
        
        for idx, row in source_docs.iterrows():
            # Reconstruct file path based on doc_id
            doc_num = row['doc_id'].split('_')[-1]  # Extract number from doc_id
            file_path = f"data/raw/{source}/doc_{doc_num}.txt"
            
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                    
                    if text.strip():  # Only add non-empty texts
                        # Create chunk with metadata
                        chunk = {
                            'text': text,
                            'metadata': {
                                'doc_id': row['doc_id'],
                                'source': row['source'],
                                'file_name': row.get('file_name', ''),
                                'document_type': row.get('document_type', ''),
                                'language': row.get('language', 'en'),
                                'text_length': len(text),
                                'department': row.get('department', ''),
                                'category': row.get('category', ''),
                                'region': row.get('region', '')
                            }
                        }
                        chunks.append(chunk)
                        loaded_count += 1
                        
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")
                    error_count += 1
            else:
                error_count += 1
        
        chunks_by_source[source] = chunks
        print(f"  Loaded {loaded_count} chunks, {error_count} errors")
    
    total_chunks = sum(len(chunks) for chunks in chunks_by_source.values())
    print(f"\nTotal chunks loaded: {total_chunks}")
    
    if total_chunks == 0:
        raise ValueError("No chunks were loaded. Check data files and metadata.")
    
    return chunks_by_source


def build_faiss_index(
    embeddings: np.ndarray,
    index_type: str = "flat"
) -> faiss.Index:
    """
    Build FAISS index from embeddings
    
    Args:
        embeddings: Numpy array of embeddings
        index_type: Type of index ("flat", "ivf", "hnsw")
    """
    print(f"\nBuilding FAISS index...")
    print(f"Index type: {index_type}")
    print(f"Embeddings shape: {embeddings.shape}")
    
    dimension = embeddings.shape[1]
    
    if index_type == "flat":
        # Simple flat index (exact search)
        index = faiss.IndexFlatIP(dimension)  # Inner Product (cosine similarity)
        
    elif index_type == "ivf":
        # IVF index (approximate search, faster for large datasets)
        nlist = min(100, embeddings.shape[0] // 10)  # Number of clusters
        quantizer = faiss.IndexFlatIP(dimension)
        index = faiss.IndexIVFFlat(quantizer, dimension, nlist)
        
        # Train the index
        print("Training IVF index...")
        index.train(embeddings.astype(np.float32))
        
    else:
        raise ValueError(f"Unsupported index type: {index_type}")
    
    # Add embeddings to index
    print("Adding embeddings to index...")
    index.add(embeddings.astype(np.float32))
    
    print(f"Index built successfully!")
    print(f"Total vectors in index: {index.ntotal}")
    
    return index


def save_faiss_index(
    index: faiss.Index,
    chunks: List[Dict],
    output_dir: str = "data/processed"
):
    """
    Save FAISS index and associated metadata
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save FAISS index
    index_path = os.path.join(output_dir, "faiss_index.bin")
    faiss.write_index(index, index_path)
    
    # Save chunk metadata
    metadata_path = os.path.join(output_dir, "index_metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=2)
    
    # Save index summary
    summary = {
        "total_vectors": index.ntotal,
        "dimension": index.d,
        "index_type": type(index).__name__,
        "total_chunks": len(chunks)
    }
    
    summary_path = os.path.join(output_dir, "index_summary.json")
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nFAISS index saved to: {index_path}")
    print(f"Metadata saved to: {metadata_path}")
    print(f"Summary saved to: {summary_path}")


def load_faiss_index(
    input_dir: str = "data/processed"
) -> Tuple[faiss.Index, List[Dict]]:
    """
    Load FAISS index and metadata
    """
    index_path = os.path.join(input_dir, "faiss_index.bin")
    metadata_path = os.path.join(input_dir, "index_metadata.json")
    
    if not os.path.exists(index_path):
        raise FileNotFoundError(f"FAISS index not found: {index_path}")
    
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")
    
    # Load index
    index = faiss.read_index(index_path)
    
    # Load metadata
    with open(metadata_path, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"Loaded FAISS index with {index.ntotal} vectors")
    print(f"Loaded metadata for {len(chunks)} chunks")
    
    return index, chunks


def main():
    """
    Main function to build complete vector database
    """
    print("=" * 70)
    print("HR & Compliance RAG System - Week 2: Vector Database Builder")
    print("=" * 70)
    
    try:
        # Step 1: Load chunks from Week 1
        print("\nStep 1: Loading chunks from Week 1...")
        chunks_by_source = load_chunks_from_week1()
        
        # Step 2: Generate embeddings
        print("\nStep 2: Generating embeddings...")
        model = load_embedding_model()
        embeddings, enriched_chunks = generate_embeddings_from_sources(
            chunks_by_source,
            model=model,
            batch_size=32
        )
        
        # Step 3: Validate embeddings
        print("\nStep 3: Validating embeddings...")
        validate_embeddings(embeddings, expected_dim=384)
        
        # Step 4: Build FAISS index
        print("\nStep 4: Building FAISS index...")
        index = build_faiss_index(embeddings, index_type="flat")
        
        # Step 5: Save everything
        print("\nStep 5: Saving vector database...")
        save_embeddings(embeddings, enriched_chunks)
        save_faiss_index(index, enriched_chunks)
        
        print("\n" + "=" * 70)
        print("Vector Database Build Complete!")
        print("=" * 70)
        print(f"Total vectors: {index.ntotal}")
        print(f"Dimension: {index.d}")
        print(f"Files saved to: data/processed/")
        print("  - embeddings.npy")
        print("  - faiss_index.bin")
        print("  - chunks_metadata.json")
        print("  - index_metadata.json")
        
    except Exception as e:
        print(f"\nError building vector database: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()