"""
Embedding Generator for HR & Compliance RAG System
Generates embeddings from chunked documents using sentence-transformers
"""

import os
import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer

# ==========================================================
# CONFIGURATION
# ==========================================================

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ==========================================================
# MODEL LOADING
# ==========================================================

def load_embedding_model(model_name: str = DEFAULT_MODEL) -> SentenceTransformer:
    """
    Load sentence-transformer embedding model
    """
    print(f"\nLoading embedding model: {model_name}")
    model = SentenceTransformer(model_name)
    print(f"Model loaded successfully.")
    print(f"Embedding dimension: {model.get_sentence_embedding_dimension()}\n")
    return model


def get_embedding_dimension(model: SentenceTransformer) -> int:
    """
    Get embedding dimension from model
    """
    return model.get_sentence_embedding_dimension()


# ==========================================================
# EMBEDDING GENERATION
# ==========================================================

def generate_embeddings(
    chunks: List[Dict],
    model: Optional[SentenceTransformer] = None,
    batch_size: int = 32,
    show_progress: bool = True
) -> Tuple[np.ndarray, List[Dict]]:
    """
    Generate embeddings for list of chunk dictionaries.
    
    Each chunk must contain:
        {
            "text": "...",
            "metadata": {...}
        }
    """

    if model is None:
        model = load_embedding_model()

    if not chunks:
        raise ValueError("No chunks provided for embedding generation.")

    texts = [chunk["text"] for chunk in chunks]

    print(f"Generating embeddings for {len(texts)} chunks...")
    print(f"Batch size: {batch_size}")

    embeddings = model.encode(
        
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
        normalize_embeddings=True  # Important for cosine similarity
    )

    expected_dim = get_embedding_dimension(model)
    actual_dim = embeddings.shape[1]

    if actual_dim != expected_dim:
        raise ValueError(
            f"Dimension mismatch! Expected {expected_dim}, got {actual_dim}"
        )

    print(f"Embeddings generated successfully.")
    print(f"Shape: {embeddings.shape}\n")

    # Attach embedding ID to each chunk
    enriched_chunks = []
    for idx, chunk in enumerate(chunks):
        enriched_chunk = chunk.copy()
        enriched_chunk["embedding_id"] = idx
        enriched_chunk["embedding_dim"] = actual_dim
        enriched_chunks.append(enriched_chunk)

    return embeddings, enriched_chunks


# ==========================================================
# MULTI-SOURCE EMBEDDING GENERATION
# ==========================================================

def generate_embeddings_from_sources(
    chunks_by_source: Dict[str, List[Dict]],
    model: Optional[SentenceTransformer] = None,
    batch_size: int = 32
) -> Tuple[np.ndarray, List[Dict]]:
    """
    Generate embeddings for multiple document sources
    """

    if model is None:
        model = load_embedding_model()

    all_embeddings = []
    all_chunks = []

    for source, chunks in chunks_by_source.items():
        print(f"\nProcessing source: {source}")
        print("-" * 50)

        embeddings, enriched_chunks = generate_embeddings(
            chunks,
            model=model,
            batch_size=batch_size
        )

        all_embeddings.append(embeddings)
        all_chunks.extend(enriched_chunks)

    final_embeddings = np.vstack(all_embeddings)

    print("\n===============================================")
    print("TOTAL EMBEDDINGS GENERATED")
    print("===============================================")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Embedding dimension: {final_embeddings.shape[1]}")
    print(f"Final shape: {final_embeddings.shape}")
    print("===============================================\n")

    return final_embeddings, all_chunks


# ==========================================================
# SAVE / LOAD FUNCTIONS
# ==========================================================

def save_embeddings(
    embeddings: np.ndarray,
    chunks: List[Dict],
    output_dir: str = "data/processed"
):
    """
    Save embeddings and metadata
    """

    os.makedirs(output_dir, exist_ok=True)

    embeddings_path = os.path.join(output_dir, "embeddings.npy")
    metadata_path = os.path.join(output_dir, "chunks_metadata.json")
    summary_path = os.path.join(output_dir, "embeddings_summary.json")

    np.save(embeddings_path, embeddings)

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2)

    summary = {
        "total_chunks": len(chunks),
        "embedding_shape": list(embeddings.shape),
        "embedding_dimension": embeddings.shape[1]
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("Embeddings and metadata saved successfully.")


def load_embeddings(
    input_dir: str = "data/processed"
) -> Tuple[np.ndarray, List[Dict]]:
    """
    Load embeddings and metadata
    """

    embeddings_path = os.path.join(input_dir, "embeddings.npy")
    metadata_path = os.path.join(input_dir, "chunks_metadata.json")

    embeddings = np.load(embeddings_path)

    with open(metadata_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    print(f"Loaded {len(chunks)} chunks.")
    print(f"Embedding shape: {embeddings.shape}")

    return embeddings, chunks


# ==========================================================
# VALIDATION FUNCTION
# ==========================================================

def validate_embeddings(
    embeddings: np.ndarray,
    expected_dim: int = 384
):
    """
    Validate embedding quality and consistency
    """

    print("\nValidating embeddings...")

    if embeddings.ndim != 2:
        raise ValueError("Embeddings must be a 2D array.")

    if embeddings.shape[1] != expected_dim:
        raise ValueError(
            f"Dimension mismatch! Expected {expected_dim}, got {embeddings.shape[1]}"
        )

    if np.isnan(embeddings).any():
        raise ValueError("Embeddings contain NaN values.")

    if np.isinf(embeddings).any():
        raise ValueError("Embeddings contain Inf values.")

    norms = np.linalg.norm(embeddings, axis=1)

    print(f"Min norm: {norms.min():.4f}")
    print(f"Max norm: {norms.max():.4f}")
    print(f"Mean norm: {norms.mean():.4f}")

    print("Embeddings validated successfully.\n")