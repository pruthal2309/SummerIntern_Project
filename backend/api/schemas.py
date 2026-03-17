"""
Pydantic schemas for the HR & Compliance RAG API
Request / response models for all endpoints.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ======================================================================
# Request models
# ======================================================================

class QueryRequest(BaseModel):
    """POST /query request body."""
    question: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The HR or compliance question to answer.",
        json_schema_extra={"example": "What is the maternity leave policy?"},
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=20,
        description="Number of documents to retrieve.",
    )
    filters: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional metadata filters, e.g. {\"category\": \"Compliance\"}.",
    )


# ======================================================================
# Response models
# ======================================================================

class SourceDocument(BaseModel):
    """A single retrieved source document reference."""
    doc_id: str = Field(description="Unique document identifier.")
    source: str = Field(description="Source collection name.")
    category: str = Field(default="", description="Document category.")
    similarity_score: float = Field(description="Cosine similarity score.")
    text_preview: str = Field(description="First ~200 characters of the chunk text.")


class QueryMetadata(BaseModel):
    """Metadata about the query processing."""
    model: str = Field(default="", description="LLM model used.")
    usage: Dict = Field(default_factory=dict, description="Token usage stats.")
    retrieval_count: int = Field(default=0, description="Number of documents retrieved.")
    total_latency_ms: float = Field(default=0, description="Total pipeline latency (ms).")
    retrieval_latency_ms: float = Field(default=0, description="Retrieval step latency (ms).")
    llm_latency_ms: float = Field(default=0, description="LLM generation latency (ms).")
    error: Optional[bool] = Field(default=None, description="True if an error occurred.")


class QueryResponse(BaseModel):
    """POST /query response body."""
    answer: str = Field(description="Generated answer grounded in the retrieved documents.")
    sources: List[SourceDocument] = Field(
        default_factory=list,
        description="Source documents used to generate the answer.",
    )
    metadata: QueryMetadata = Field(
        default_factory=QueryMetadata,
        description="Processing metadata.",
    )


class ServiceStatus(BaseModel):
    """Status of a single sub-service."""
    status: Optional[str] = None
    total_vectors: Optional[int] = None
    embedding_dimension: Optional[int] = None
    index_type: Optional[str] = None
    total_chunks: Optional[int] = None
    available: Optional[bool] = None
    model: Optional[str] = None
    max_tokens: Optional[int] = None

    class Config:
        extra = "allow"


class HealthResponse(BaseModel):
    """GET /health response body."""
    status: str = Field(description="Overall system health: 'healthy' or 'degraded'.")
    vector_db: Dict = Field(default_factory=dict, description="Vector database status.")
    llm: Dict = Field(default_factory=dict, description="LLM service status.")
    api: Dict = Field(default_factory=dict, description="API status.")
