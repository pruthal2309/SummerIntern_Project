"""
Main script to load and process documents for Week 1
Performs dataset ingestion, validation, chunking, and metadata creation
"""

import os
import json
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ingestion.loaders import load_all_documents
from ingestion.validator import validate_documents, filter_valid_documents
from ingestion.chunker import chunk_documents
from ingestion.metadata_builder import build_metadata_csv


def get_project_root():
    """Get the project root directory"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # If we're in ingestion folder, go up one level
    if os.path.basename(current_dir) == 'ingestion':
        return os.path.dirname(current_dir)
    return current_dir


def main():
    """
    Main function to execute Week 1 tasks:
    1. Load documents from data/raw
    2. Validate documents
    3. Chunk documents
    4. Build metadata CSV
    """
    
    try:
        print("=" * 60)
        print("HR & Compliance RAG System - Week 1 Data Ingestion")
        print("=" * 60)
        print()
        
        # Get project root and set paths
        project_root = get_project_root()
        data_raw = os.path.join(project_root, 'data', 'raw')
        data_processed = os.path.join(project_root, 'data', 'processed')
        metadata_path = os.path.join(project_root, 'data', 'metadata.csv')
        
        print(f"Project root: {project_root}")
        print(f"Data directory: {data_raw}")
        print(f"Data directory exists: {os.path.exists(data_raw)}")
        print()
        
        if not os.path.exists(data_raw):
            raise FileNotFoundError(f"Data directory not found: {data_raw}")
        
        # Step 1: Load all documents
        print("Step 1: Loading documents...")
        print("-" * 60)
        all_documents = load_all_documents(data_raw)
        
        total_docs = sum(len(docs) for docs in all_documents.values())
        print(f"\nTotal documents loaded: {total_docs}")
        
        if total_docs == 0:
            raise ValueError("No documents were loaded. Check data directory.")
        
        print()
        
        # Step 2: Validate documents
        print("Step 2: Validating documents...")
        print("-" * 60)
        
        for source, documents in all_documents.items():
            stats = validate_documents(documents)
            print(f"\n{source}:")
            print(f"  Total: {stats['total']}")
            print(f"  Valid: {stats['valid']}")
            print(f"  Invalid: {stats['invalid']}")
            print(f"  Valid %: {stats['valid_percentage']:.2f}%")
            
            # Filter to keep only valid documents
            all_documents[source] = filter_valid_documents(documents)
        
        print()
        
        # Step 3: Chunk documents
        print("Step 3: Chunking documents...")
        print("-" * 60)
        
        all_chunks = {}
        total_chunks = 0
        
        for source, documents in all_documents.items():
            chunks = chunk_documents(documents, chunk_size=1000, overlap=200)
            all_chunks[source] = chunks
            total_chunks += len(chunks)
            print(f"{source}: {len(chunks)} chunks created")
        
        print(f"\nTotal chunks: {total_chunks}")
        print()
        
        # Step 4: Build metadata
        print("Step 4: Building metadata...")
        print("-" * 60)
        metadata_df = build_metadata_csv(all_documents, metadata_path)
        print()
        
        # Step 5: Save processed data summary
        print("Step 5: Saving summary...")
        print("-" * 60)
        
        summary = {
            'total_documents': total_docs,
            'total_chunks': total_chunks,
            'sources': {
                source: {
                    'documents': len(docs),
                    'chunks': len(all_chunks[source])
                }
                for source, docs in all_documents.items()
            }
        }
        
        # Create processed directory if it doesn't exist
        os.makedirs(data_processed, exist_ok=True)
        
        summary_path = os.path.join(data_processed, 'ingestion_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"Summary saved to {summary_path}")
        print()
        
        print("=" * 60)
        print("Week 1 Data Ingestion Complete!")
        print("=" * 60)
        print("\nResults:")
        print(f"  - Documents loaded: {total_docs}")
        print(f"  - Chunks created: {total_chunks}")
        print(f"  - Metadata file: {metadata_path}")
        print(f"  - Summary file: {summary_path}")
        
    except Exception as e:
        print(f"\n❌ Week 1 ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
