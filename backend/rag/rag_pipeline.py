"""
RAG Pipeline Orchestrator for HR & Compliance System
Wires together Retrieval → Prompt Builder → Groq LLM into a single call.
"""

import os
import time
import logging
from typing import Dict, List, Optional

from dotenv import load_dotenv

from .retrieval_service import RetrievalService
from .prompt_builder import PromptBuilder
from .llm_service import GroqLLMService

load_dotenv()
logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    End-to-end Retrieval-Augmented Generation pipeline.

    Flow:
        question → vector retrieval → prompt construction → LLM generation → response
    """

    def __init__(
        self,
        retrieval_service: Optional[RetrievalService] = None,
        prompt_builder: Optional[PromptBuilder] = None,
        llm_service: Optional[GroqLLMService] = None,
        default_top_k: int = 5,
    ):
        self.retrieval = retrieval_service or RetrievalService()
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.llm = llm_service or GroqLLMService()
        self.default_top_k = int(os.getenv("RAG_TOP_K", str(default_top_k)))

        logger.info("RAGPipeline initialised  default_top_k=%d", self.default_top_k)

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def answer(
        self,
        question: str,
        top_k: Optional[int] = None,
        filters: Optional[Dict] = None,
    ) -> Dict:
        """
        Generate a grounded answer for the given question.

        Args:
            question: User question text.
            top_k: Number of documents to retrieve (default from config).
            filters: Optional metadata filters for retrieval.

        Returns:
            {
                "answer": str,
                "sources": [{"doc_id", "source", "category", "similarity_score", "text_preview"}],
                "metadata": {
                    "model": str,
                    "usage": dict,
                    "retrieval_count": int,
                    "total_latency_ms": float,
                    "retrieval_latency_ms": float,
                    "llm_latency_ms": float,
                },
            }
        """
        total_start = time.time()
        effective_top_k = top_k or self.default_top_k

        # ---- Step 1: Validate input ----
        if not question or not question.strip():
            return self._empty_answer("Please provide a non-empty question.")

        question = question.strip()

        # ---- Step 2: Retrieve relevant documents ----
        retrieval_start = time.time()
        try:
            chunks = self.retrieval.retrieve(question, top_k=effective_top_k, filters=filters)
            logger.info(f"Retrieved {len(chunks)} chunks for query: '{question[:50]}...'")
            
            # Debug: Log similarity scores if we have results
            if chunks:
                scores = [chunk.get('similarity_score', 0) for chunk in chunks]
                logger.info(f"Similarity scores: min={min(scores):.4f}, max={max(scores):.4f}, avg={sum(scores)/len(scores):.4f}")
            
        except Exception as exc:
            logger.error("Retrieval failed: %s", exc)
            return self._error_answer(f"Document retrieval failed: {exc}")
        retrieval_ms = (time.time() - retrieval_start) * 1000

        # Handle no results
        if not chunks:
            logger.warning("No documents retrieved for query: %s", question[:80])
            
            # Debug: Try a broader search to see if the issue is with the specific query
            try:
                debug_chunks = self.retrieval.retrieve("council decision", top_k=5)
                logger.info(f"Debug search for 'council decision' returned {len(debug_chunks)} results")
                if debug_chunks:
                    debug_scores = [chunk.get('similarity_score', 0) for chunk in debug_chunks]
                    logger.info(f"Debug similarity scores: {debug_scores}")
            except Exception as e:
                logger.error(f"Debug search failed: {e}")
            
            return self._empty_answer(
                "I could not find any relevant documents to answer your question. "
                "Please try rephrasing or broadening your query."
            )

        # ---- Step 3: Build prompt ----
        messages = self.prompt_builder.build_messages(question, chunks)

        # ---- Step 4: Call LLM ----
        try:
            llm_result = self.llm.generate(messages)
        except Exception as exc:
            logger.error("LLM generation failed: %s", exc)
            return self._error_answer(f"LLM generation failed: {exc}")

        total_ms = (time.time() - total_start) * 1000

        # ---- Step 5: Build response ----
        sources = self._build_sources(chunks)

        return {
            "answer": llm_result["answer"],
            "sources": sources,
            "metadata": {
                "model": llm_result.get("model", ""),
                "usage": llm_result.get("usage", {}),
                "retrieval_count": len(chunks),
                "total_latency_ms": round(total_ms, 2),
                "retrieval_latency_ms": round(retrieval_ms, 2),
                "llm_latency_ms": llm_result.get("latency_ms", 0),
            },
        }

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health_check(self) -> Dict:
        """Aggregate health from sub-services."""
        retrieval_health = self.retrieval.health_check()
        llm_health = self.llm.health_check()

        all_healthy = (
            retrieval_health.get("total_vectors", 0) > 0
            and llm_health.get("available", False)
        )

        return {
            "status": "healthy" if all_healthy else "degraded",
            "vector_db": retrieval_health,
            "llm": llm_health,
            "api": {"status": "running"},
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_sources(chunks: List[Dict]) -> List[Dict]:
        """Extract a concise source summary from retrieved chunks."""
        sources = []
        for chunk in chunks:
            meta = chunk.get("metadata", {})
            text = chunk.get("text", "")
            sources.append({
                "doc_id": meta.get("doc_id", "N/A"),
                "source": meta.get("source", "unknown"),
                "category": meta.get("category", ""),
                "similarity_score": round(chunk.get("similarity_score", 0.0), 4),
                "text_preview": text[:200] + ("..." if len(text) > 200 else ""),
            })
        return sources

    @staticmethod
    def _empty_answer(message: str) -> Dict:
        return {
            "answer": message,
            "sources": [],
            "metadata": {"retrieval_count": 0},
        }

    @staticmethod
    def _error_answer(message: str) -> Dict:
        return {
            "answer": f"An error occurred: {message}",
            "sources": [],
            "metadata": {"error": True},
        }
