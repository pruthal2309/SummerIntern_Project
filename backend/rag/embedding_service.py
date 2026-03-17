"""
Embedding Service for HR & Compliance RAG System
Thin singleton wrapper around the Week 2 embedding model for query encoding.
"""

import logging
import numpy as np
from typing import Optional

from sentence_transformers import SentenceTransformer
from backend.vectorstore.embedding_generator import load_embedding_model

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Manages a singleton embedding model and provides query encoding.
    Re-uses the same model instance across the application lifetime.
    """

    _instance: Optional["EmbeddingService"] = None
    _model: Optional[SentenceTransformer] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, model_name: Optional[str] = None):
        if self._model is not None:
            return  # already initialised
        self._model = load_embedding_model(model_name) if model_name else load_embedding_model()
        self.dimension = self._model.get_sentence_embedding_dimension()
        logger.info("EmbeddingService initialised  dim=%d", self.dimension)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def encode_query(self, query: str) -> np.ndarray:
        """
        Encode a single query string into an embedding vector.

        Args:
            query: Query text.

        Returns:
            1-D numpy array of shape (dimension,).
        """
        embedding = self._model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )
        return embedding

    @property
    def model(self) -> SentenceTransformer:
        return self._model
