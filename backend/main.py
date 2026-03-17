"""
Backend Entry Point for HR & Compliance RAG System
Handles pipeline execution and API server startup
"""

import os
import sys
import argparse
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import config


def run_pipeline(skip_week1=False, skip_week2=False):
    """Run the data processing pipeline"""
    print("🚀 Starting RAG Pipeline")
    print("=" * 60)
    
    # Week 1: Data Ingestion
    if not skip_week1:
        print("\n📥 Week 1: Data Ingestion")
        print("-" * 60)
        from backend.ingestion.load_documents import main as week1_main
        week1_main()
    else:
        print("\n⏭️  Skipping Week 1 (Data Ingestion)")
    
    # Week 2: Embeddings and Vector Index
    if not skip_week2:
        print("\n🧠 Week 2: Embeddings & Vector Index")
        print("-" * 60)
        from backend.vectorstore.build_index import load_chunks_from_week1, build_faiss_index, save_faiss_index
        from backend.vectorstore.embedding_generator import (
            load_embedding_model,
            generate_embeddings_from_sources,
            validate_embeddings,
            save_embeddings
        )
        
        # Load chunks
        print("Loading chunks from Week 1...")
        chunks_by_source = load_chunks_from_week1()
        
        # Generate embeddings
        print("Generating embeddings...")
        model = load_embedding_model()
        embeddings, enriched_chunks = generate_embeddings_from_sources(
            chunks_by_source,
            model=model,
            batch_size=config.BATCH_SIZE
        )
        
        # Validate embeddings
        print("Validating embeddings...")
        validate_embeddings(embeddings, expected_dim=config.EMBEDDING_DIMENSION)
        
        # Save embeddings
        print("Saving embeddings...")
        save_embeddings(embeddings, enriched_chunks)
        
        # Build FAISS index
        print("Building FAISS index...")
        index = build_faiss_index(embeddings, index_type=config.FAISS_INDEX_TYPE)
        
        # Save index
        print("Saving FAISS index...")
        save_faiss_index(index, enriched_chunks)
        
        print("\n✅ Week 2 completed successfully!")
    else:
        print("\n⏭️  Skipping Week 2 (Embeddings & Index)")
    
    print("\n🎉 Pipeline completed successfully!")


def query_rag(question: str, top_k: int = 5, filters: Optional[Dict] = None) -> Dict:
    """Query the RAG system directly (for Streamlit integration)"""
    from backend.rag.rag_pipeline import RAGPipeline
    
    pipeline = RAGPipeline()
    return pipeline.answer(question=question, top_k=top_k, filters=filters)


def run_server(host=None, port=None):
    """Start the FastAPI server"""
    import uvicorn
    
    host = host or config.API_HOST
    port = port or config.API_PORT
    
    print(f"\n🌐 Starting HR & Compliance RAG API")
    print("=" * 60)
    print(f"📡 Server: http://{host}:{port}")
    print(f"📖 API Docs: http://{host}:{port}/docs")
    print(f"❤️  Health: http://{host}:{port}/health")
    print("\n⏹️  Press Ctrl+C to stop")
    print("=" * 60)
    
    # Import app from backend
    from backend.api.app import app
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


def validate_config():
    """Validate configuration"""
    print("🔍 Validating configuration...")
    errors = config.validate()
    
    if errors:
        print("\n❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        return False
    
    print("✅ Configuration valid")
    return True


def show_config():
    """Display configuration summary"""
    import json
    
    print("\n📋 Configuration Summary")
    print("=" * 60)
    summary = config.get_summary()
    print(json.dumps(summary, indent=2))
    print("=" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="HR & Compliance RAG System - Backend"
    )
    
    # Pipeline options
    parser.add_argument(
        '--pipeline',
        action='store_true',
        help='Run the data processing pipeline'
    )
    parser.add_argument(
        '--no-week1',
        action='store_true',
        help='Skip Week 1 (data ingestion)'
    )
    parser.add_argument(
        '--no-week2',
        action='store_true',
        help='Skip Week 2 (embeddings & index)'
    )
    
    # Server options
    parser.add_argument(
        '--serve',
        action='store_true',
        help='Start the API server'
    )
    parser.add_argument(
        '--host',
        type=str,
        default=None,
        help='API server host'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='API server port'
    )
    
    # Utility options
    parser.add_argument(
        '--config',
        action='store_true',
        help='Show configuration summary'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate configuration only'
    )
    
    args = parser.parse_args()
    
    # Show config
    if args.config:
        show_config()
        return
    
    # Validate config
    if args.validate:
        validate_config()
        return
    
    # Start server
    if args.serve:
        if not validate_config():
            print("\n⚠️  Fix configuration errors before starting server")
            sys.exit(1)
        run_server(host=args.host, port=args.port)
        return
    
    # Run pipeline
    if args.pipeline or (not args.serve and not args.config and not args.validate):
        if not validate_config():
            print("\n⚠️  Fix configuration errors before running pipeline")
            sys.exit(1)
        run_pipeline(skip_week1=args.no_week1, skip_week2=args.no_week2)
        return
    
    # If no action specified, show help
    parser.print_help()


if __name__ == "__main__":
    main()
