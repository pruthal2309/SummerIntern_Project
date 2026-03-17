"""
Retrieval Service for HR & Compliance RAG System
Wraps the Week 2 SemanticRetriever and MetadataFilter for use in the RAG pipeline.
"""

import logging
from typing import Dict, List, Optional

from backend.vectorstore.retriever import SemanticRetriever, load_retriever
from backend.vectorstore.metadata_filter import MetadataFilter

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    High-level retrieval interface used by the RAG pipeline.
    Encapsulates vector search + metadata filtering in a single call.
    """

    def __init__(
        self,
        retriever: Optional[SemanticRetriever] = None,
        index_path: str = "data/processed/faiss_index.bin",
        metadata_path: str = "data/processed/index_metadata.json",
    ):
        """
        Args:
            retriever: Pre-built SemanticRetriever instance (optional).
            index_path: Path to FAISS index binary.
            metadata_path: Path to index metadata JSON.
        """
        self.retriever = retriever or load_retriever(index_path, metadata_path)
        logger.info("RetrievalService initialised  chunks=%d", len(self.retriever.chunks))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Retrieve relevant document chunks for a given query.

        Args:
            query: User question.
            top_k: Number of results to retrieve from the vector index.
            filters: Optional dict of metadata filters, e.g.
                     {"category": "Compliance", "region": "Global"}.

        Returns:
            List of chunk dicts with text, metadata, and similarity_score.
        """
        # Fetch more candidates when filters are active so we still have
        # enough results after filtering.
        fetch_k = top_k * 3 if filters else top_k

        results = self.retriever.search(query, top_k=fetch_k)

        if filters:
            results = self._apply_filters(results, filters)

        # Trim to requested top_k after filtering
        results = results[:top_k]

        logger.info(
            "Retrieved %d chunks for query (top_k=%d, filters=%s)",
            len(results), top_k, bool(filters),
        )
        return results

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def health_check(self) -> Dict:
        """Return basic stats about the loaded index."""
        return self.retriever.get_index_stats()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _apply_filters(chunks: List[Dict], filters: Dict) -> List[Dict]:
        """Apply metadata filters to search results."""
        meta_filter = MetadataFilter()

        for field, value in filters.items():
            if isinstance(value, list):
                meta_filter.add_filter(field, value, operator="in")
            elif isinstance(value, str):
                meta_filter.add_filter(field, value, operator="equals")
            else:
                meta_filter.add_filter(field, value, operator="equals")

        return meta_filter.apply(chunks)
