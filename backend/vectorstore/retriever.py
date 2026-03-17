"""
Semantic Retriever for HR & Compliance RAG System
Performs similarity search and retrieves relevant documents
"""

import os
import json
import numpy as np
import faiss
from typing import List, Dict, Tuple, Optional
from sentence_transformers import SentenceTransformer

from backend.vectorstore.embedding_generator import load_embedding_model, get_embedding_dimension


# ==========================================================
# SIMILARITY SEARCH
# ==========================================================

class SemanticRetriever:
    """
    Semantic retriever using FAISS vector database
    Performs similarity search on embedded documents
    """
    
    def __init__(
        self,
        index: Optional[faiss.Index] = None,
        chunks: Optional[List[Dict]] = None,
        model: Optional[SentenceTransformer] = None,
        index_path: str = "data/processed/faiss_index.bin",
        metadata_path: str = "data/processed/index_metadata.json"
    ):
        """
        Initialize retriever
        
        Args:
            index: FAISS index object
            chunks: List of chunk metadata
            model: Embedding model
            index_path: Path to pre-built FAISS index
            metadata_path: Path to index metadata
        """
        self.model = model or load_embedding_model()
        self.embedding_dim = get_embedding_dimension(self.model)
        
        # Load index and metadata if not provided
        if index is None or chunks is None:
            self.index, self.chunks = self._load_index_and_metadata(
                index_path, metadata_path
            )
        else:
            self.index = index
            self.chunks = chunks
        
        print(f"Retriever initialized with {len(self.chunks)} chunks")
    
    def _load_index_and_metadata(
        self,
        index_path: str,
        metadata_path: str
    ) -> Tuple[faiss.Index, List[Dict]]:
        """
        Load FAISS index and metadata from disk
        
        Args:
            index_path: Path to FAISS index binary
            metadata_path: Path to metadata JSON
            
        Returns:
            Tuple of (FAISS index, chunks list)
        """
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"FAISS index not found: {index_path}")
        
        if not os.path.exists(metadata_path):
            raise FileNotFoundError(f"Metadata not found: {metadata_path}")
        
        print(f"Loading FAISS index from {index_path}")
        index = faiss.read_index(index_path)
        
        print(f"Loading metadata from {metadata_path}")
        with open(metadata_path, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
        
        print(f"Index loaded: {index.ntotal} vectors, dimension {index.d}")
        return index, chunks
    
    def _embed_query(self, query: str) -> np.ndarray:
        """
        Convert query text to embedding
        
        Args:
            query: Query text
            
        Returns:
            Query embedding as numpy array
        """
        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embedding.reshape(1, -1).astype(np.float32)
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        return_scores: bool = True
    ) -> List[Dict]:
        """
        Perform semantic similarity search
        
        Args:
            query: Query text
            top_k: Number of top results to retrieve
            return_scores: Whether to include similarity scores
            
        Returns:
            List of retrieved chunks with metadata and scores
        """
        # Generate query embedding
        query_embedding = self._embed_query(query)
        
        # Search in FAISS index
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Flatten scores and indices
        scores = scores[0]
        indices = indices[0]
        
        # Retrieve chunks and format results
        results = []
        for rank, (idx, score) in enumerate(zip(indices, scores)):
            if idx < 0 or idx >= len(self.chunks):
                continue
            
            chunk = self.chunks[int(idx)].copy()
            chunk['search_rank'] = rank + 1
            chunk['similarity_score'] = float(score)
            
            if return_scores:
                results.append(chunk)
            else:
                results.append(chunk)
        
        return results
    
    def batch_search(
        self,
        queries: List[str],
        top_k: int = 5
    ) -> List[List[Dict]]:
        """
        Perform batch similarity search for multiple queries
        
        Args:
            queries: List of query texts
            top_k: Number of top results per query
            
        Returns:
            List of result lists (one per query)
        """
        all_results = []
        
        for query in queries:
            results = self.search(query, top_k=top_k)
            all_results.append(results)
        
        return all_results
    
    def get_context(
        self,
        query: str,
        top_k: int = 5,
        include_metadata: bool = True
    ) -> Dict:
        """
        Get retrieval context for a query
        
        Args:
            query: Query text
            top_k: Number of results
            include_metadata: Whether to include metadata
            
        Returns:
            Dictionary with query and retrieved context
        """
        results = self.search(query, top_k=top_k)
        
        context = {
            'query': query,
            'num_results': len(results),
            'results': []
        }
        
        for result in results:
            item = {
                'text': result.get('text', ''),
                'similarity_score': result.get('similarity_score', 0.0),
                'search_rank': result.get('search_rank', 0)
            }
            
            if include_metadata:
                item['metadata'] = result.get('metadata', {})
            
            context['results'].append(item)
        
        return context
    
    def retrieve_by_doc_id(
        self,
        doc_id: str
    ) -> Optional[Dict]:
        """
        Retrieve specific document by ID
        
        Args:
            doc_id: Document ID
            
        Returns:
            Chunk data if found, None otherwise
        """
        for chunk in self.chunks:
            if chunk.get('metadata', {}).get('doc_id') == doc_id:
                return chunk
        
        return None
    
    def get_chunk_by_index(self, idx: int) -> Optional[Dict]:
        """
        Get chunk by its index in the vector database
        
        Args:
            idx: Chunk index
            
        Returns:
            Chunk data if found, None otherwise
        """
        if 0 <= idx < len(self.chunks):
            return self.chunks[idx]
        return None
    
    def get_index_stats(self) -> Dict:
        """
        Get statistics about the vector index
        
        Returns:
            Dictionary with index statistics
        """
        return {
            'total_vectors': self.index.ntotal,
            'embedding_dimension': self.index.d,
            'index_type': type(self.index).__name__,
            'total_chunks': len(self.chunks)
        }
    
    def benchmark_search(
        self,
        queries: List[str],
        top_k: int = 5
    ) -> Dict:
        """
        Benchmark search performance
        
        Args:
            queries: List of test queries
            top_k: Number of results per query
            
        Returns:
            Dictionary with benchmark results
        """
        import time
        
        search_times = []
        embedding_times = []
        
        for query in queries:
            # Time embedding generation
            start = time.time()
            query_embedding = self._embed_query(query)
            embedding_time = time.time() - start
            embedding_times.append(embedding_time)
            
            # Time FAISS search
            start = time.time()
            scores, indices = self.index.search(query_embedding, top_k)
            search_time = time.time() - start
            search_times.append(search_time)
        
        return {
            'num_queries': len(queries),
            'top_k': top_k,
            'avg_embedding_time_ms': np.mean(embedding_times) * 1000,
            'avg_search_time_ms': np.mean(search_times) * 1000,
            'total_time_ms': (np.sum(embedding_times) + np.sum(search_times)) * 1000,
            'latency_stats': {
                'embedding': {
                    'min': np.min(embedding_times) * 1000,
                    'max': np.max(embedding_times) * 1000,
                    'mean': np.mean(embedding_times) * 1000,
                    'std': np.std(embedding_times) * 1000
                },
                'search': {
                    'min': np.min(search_times) * 1000,
                    'max': np.max(search_times) * 1000,
                    'mean': np.mean(search_times) * 1000,
                    'std': np.std(search_times) * 1000
                }
            }
        }


# ==========================================================
# UTILITY FUNCTIONS
# ==========================================================

def load_retriever(
    index_path: str = "data/processed/faiss_index.bin",
    metadata_path: str = "data/processed/index_metadata.json"
) -> SemanticRetriever:
    """
    Load retriever from saved index and metadata
    
    Args:
        index_path: Path to FAISS index
        metadata_path: Path to metadata
        
    Returns:
        Initialized SemanticRetriever instance
    """
    return SemanticRetriever(
        index_path=index_path,
        metadata_path=metadata_path
    )


def demo_retrieval(
    retriever: SemanticRetriever,
    sample_queries: Optional[List[str]] = None
):
    """
    Demo retrieval with sample queries
    
    Args:
        retriever: SemanticRetriever instance
        sample_queries: List of sample queries
    """
    if sample_queries is None:
        sample_queries = [
            "What are the leave policies?",
            "Tell me about compliance requirements",
            "What is the grievance procedure?",
            "Employee compensation structure",
            "Remote work policy"
        ]
    
    print("\n" + "=" * 70)
    print("RETRIEVAL DEMO")
    print("=" * 70)
    
    for query in sample_queries:
        print(f"\nQuery: {query}")
        print("-" * 70)
        
        results = retriever.search(query, top_k=3)
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"  Similarity Score: {result['similarity_score']:.4f}")
            
            text = result.get('text', '')
            preview = text[:200] + "..." if len(text) > 200 else text
            print(f"  Text: {preview}")
            
            metadata = result.get('metadata', {})
            if metadata:
                print(f"  Metadata:")
                print(f"    - Doc ID: {metadata.get('doc_id', 'N/A')}")
                print(f"    - Source: {metadata.get('source', 'N/A')}")
                print(f"    - Category: {metadata.get('category', 'N/A')}")


if __name__ == "__main__":
    # Demo usage
    retriever = load_retriever()
    demo_retrieval(retriever)
