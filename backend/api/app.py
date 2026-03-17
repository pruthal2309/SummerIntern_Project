"""
FastAPI Application for HR & Compliance RAG System
Main application entry point – configures middleware, routes, and startup events.
"""

import os
import sys
import logging
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is on sys.path so that `vectorstore` / `rag` resolve
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


# ======================================================================
# Lifespan – startup / shutdown
# ======================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise the RAG pipeline once when the server starts."""
    from rag.rag_pipeline import RAGPipeline
    from api.routes import set_pipeline

    logger.info("Initialising RAG pipeline …")
    try:
        pipeline = RAGPipeline()
        set_pipeline(pipeline)
        app.state.pipeline = pipeline
        logger.info("RAG pipeline ready.")
    except Exception as exc:
        logger.error("Failed to initialise RAG pipeline: %s", exc)
        # Still start the server – /health will report degraded status
        set_pipeline(None)

    yield  # application runs

    logger.info("Shutting down …")


# ======================================================================
# App factory
# ======================================================================

app = FastAPI(
    title="HR & Compliance RAG API",
    description=(
        "Enterprise Retrieval-Augmented Generation API for answering "
        "HR & compliance questions grounded in company documents.\n\n"
        "**Week 3** – LLM Integration, RAG Orchestration, and FastAPI."
    ),
    version="0.3.0",
    lifespan=lifespan,
)

# CORS – allow all origins in development; tighten for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
from api.routes import router  # noqa: E402
app.include_router(router)


# ======================================================================
# Root redirect
# ======================================================================

@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to the interactive API docs."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")
