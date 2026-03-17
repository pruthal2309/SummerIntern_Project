"""
API Routes for HR & Compliance RAG System
Defines FastAPI endpoints for query answering and health checks.
"""

import logging
from fastapi import APIRouter, HTTPException

from .schemas import QueryRequest, QueryResponse, QueryMetadata, SourceDocument, HealthResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# The pipeline is injected at startup via app.state — we access it through
# a module-level reference set by app.py.
_pipeline = None


def set_pipeline(pipeline):
    """Called by app.py during startup to inject the RAGPipeline instance."""
    global _pipeline
    _pipeline = pipeline


def _get_pipeline():
    if _pipeline is None:
        raise HTTPException(
            status_code=503,
            detail="RAG pipeline is not initialised. Server may still be starting.",
        )
    return _pipeline


# ======================================================================
# POST /query
# ======================================================================

@router.post(
    "/query",
    response_model=QueryResponse,
    summary="Ask an HR & Compliance question",
    description="Submit a question and receive an AI-generated answer grounded in HR & compliance documents.",
)
async def query(request: QueryRequest) -> QueryResponse:
    """
    Accept a user question, retrieve relevant documents, and generate
    a grounded answer using the Groq LLM.
    """
    pipeline = _get_pipeline()

    logger.info("POST /query  question='%s'  top_k=%d", request.question[:80], request.top_k)

    try:
        result = pipeline.answer(
            question=request.question,
            top_k=request.top_k,
            filters=request.filters,
        )
    except Exception as exc:
        logger.exception("Pipeline error")
        raise HTTPException(status_code=500, detail=f"Pipeline error: {exc}")

    # Map raw dicts to Pydantic models
    sources = [SourceDocument(**s) for s in result.get("sources", [])]
    metadata = QueryMetadata(**result.get("metadata", {}))

    return QueryResponse(
        answer=result["answer"],
        sources=sources,
        metadata=metadata,
    )


# ======================================================================
# GET /health
# ======================================================================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="System health check",
    description="Returns the health status of the vector database, LLM service, and API.",
)
async def health() -> HealthResponse:
    """Check the health of all sub-systems."""
    pipeline = _get_pipeline()

    try:
        status = pipeline.health_check()
    except Exception as exc:
        logger.exception("Health check error")
        return HealthResponse(
            status="degraded",
            vector_db={"error": str(exc)},
            llm={"error": str(exc)},
            api={"status": "running"},
        )

    return HealthResponse(**status)
