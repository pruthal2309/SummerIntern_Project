"""
Metadata Filter for HR & Compliance RAG System
Enables filtering of retrieved results based on metadata attributes
"""

from typing import List, Dict, Optional, Any, Callable


# ==========================================================
# METADATA FILTERING
# ==========================================================

class MetadataFilter:
    """
    Filter retrieved chunks based on metadata attributes
    Supports equality, range, and custom filtering
    """
    
    def __init__(self):
        """Initialize metadata filter"""
        self.filters = []
    
    def add_filter(
        self,
        field: str,
        value: Any = None,
        operator: str = "equals",
        custom_fn: Optional[Callable] = None
    ) -> 'MetadataFilter':
        """
        Add a filter condition
        
        Args:
            field: Metadata field name
            value: Value to filter by
            operator: Filter operator ("equals", "in", "contains", "range", "custom")
            custom_fn: Custom filter function
            
        Returns:
            Self for method chaining
        """
        self.filters.append({
            'field': field,
            'value': value,
            'operator': operator,
            'custom_fn': custom_fn
        })
        return self
    
    def clear_filters(self) -> 'MetadataFilter':
        """Clear all filters"""
        self.filters = []
        return self
    
    def apply(self, chunks: List[Dict]) -> List[Dict]:
        """
        Apply all filters to chunks
        
        Args:
            chunks: List of chunks with metadata
            
        Returns:
            Filtered list of chunks
        """
        filtered = chunks
        
        for filter_spec in self.filters:
            filtered = self._apply_single_filter(filtered, filter_spec)
        
        return filtered
    
    def _apply_single_filter(
        self,
        chunks: List[Dict],
        filter_spec: Dict
    ) -> List[Dict]:
        """
        Apply a single filter condition
        
        Args:
            chunks: List of chunks to filter
            filter_spec: Filter specification
            
        Returns:
            Filtered list
        """
        field = filter_spec['field']
        value = filter_spec['value']
        operator = filter_spec['operator']
        custom_fn = filter_spec.get('custom_fn')
        
        if operator == "equals":
            return self._filter_equals(chunks, field, value)
        elif operator == "in":
            return self._filter_in(chunks, field, value)
        elif operator == "contains":
            return self._filter_contains(chunks, field, value)
        elif operator == "range":
            return self._filter_range(chunks, field, value)
        elif operator == "custom":
            return self._filter_custom(chunks, field, custom_fn)
        else:
            raise ValueError(f"Unknown operator: {operator}")
    
    def _get_metadata_value(self, chunk: Dict, field: str) -> Any:
        """
        Extract metadata value from chunk
        
        Args:
            chunk: Chunk dictionary
            field: Field path (supports dot notation like "metadata.source")
            
        Returns:
            Field value or None
        """
        if 'metadata' in chunk:
            metadata = chunk['metadata']
            if field in metadata:
                return metadata[field]
        
        # Support direct field access
        if field in chunk:
            return chunk[field]
        
        return None
    
    def _filter_equals(
        self,
        chunks: List[Dict],
        field: str,
        value: Any
    ) -> List[Dict]:
        """Filter by exact equality"""
        return [
            chunk for chunk in chunks
            if self._get_metadata_value(chunk, field) == value
        ]
    
    def _filter_in(
        self,
        chunks: List[Dict],
        field: str,
        values: List[Any]
    ) -> List[Dict]:
        """Filter by membership in list"""
        return [
            chunk for chunk in chunks
            if self._get_metadata_value(chunk, field) in values
        ]
    
    def _filter_contains(
        self,
        chunks: List[Dict],
        field: str,
        substring: str
    ) -> List[Dict]:
        """Filter by substring containment"""
        return [
            chunk for chunk in chunks
            if isinstance(self._get_metadata_value(chunk, field), str)
            and substring.lower() in self._get_metadata_value(chunk, field).lower()
        ]
    
    def _filter_range(
        self,
        chunks: List[Dict],
        field: str,
        range_tuple: tuple
    ) -> List[Dict]:
        """Filter by range (min, max)"""
        min_val, max_val = range_tuple
        
        return [
            chunk for chunk in chunks
            if isinstance(self._get_metadata_value(chunk, field), (int, float))
            and min_val <= self._get_metadata_value(chunk, field) <= max_val
        ]
    
    def _filter_custom(
        self,
        chunks: List[Dict],
        field: str,
        custom_fn: Callable
    ) -> List[Dict]:
        """Filter using custom function"""
        return [
            chunk for chunk in chunks
            if custom_fn(self._get_metadata_value(chunk, field))
        ]


# ==========================================================
# FILTERED RETRIEVAL
# ==========================================================

class FilteredRetriever:
    """
    Retriever with metadata filtering capabilities
    Combines semantic search with metadata filtering
    """
    
    def __init__(self, base_retriever):
        """
        Initialize filtered retriever
        
        Args:
            base_retriever: Base SemanticRetriever instance
        """
        self.base_retriever = base_retriever
        self.filter = MetadataFilter()
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        apply_filter: bool = True
    ) -> List[Dict]:
        """
        Search with optional metadata filtering
        
        Args:
            query: Query text
            top_k: Number of results before filtering
            apply_filter: Whether to apply metadata filters
            
        Returns:
            Filtered search results
        """
        # Perform base semantic search
        results = self.base_retriever.search(query, top_k=top_k)
        
        # Apply metadata filters if enabled
        if apply_filter and self.filter.filters:
            results = self.filter.apply(results)
        
        return results
    
    def by_source(self, source: str) -> 'FilteredRetriever':
        """Filter by source"""
        self.filter.add_filter('source', source, operator='equals')
        return self
    
    def by_category(self, category: str) -> 'FilteredRetriever':
        """Filter by category"""
        self.filter.add_filter('category', category, operator='equals')
        return self
    
    def by_categories(self, categories: List[str]) -> 'FilteredRetriever':
        """Filter by multiple categories"""
        self.filter.add_filter('category', categories, operator='in')
        return self
    
    def by_region(self, region: str) -> 'FilteredRetriever':
        """Filter by region"""
        self.filter.add_filter('region', region, operator='equals')
        return self
    
    def by_department(self, department: str) -> 'FilteredRetriever':
        """Filter by department"""
        self.filter.add_filter('department', department, operator='equals')
        return self
    
    def by_document_type(self, doc_type: str) -> 'FilteredRetriever':
        """Filter by document type"""
        self.filter.add_filter('document_type', doc_type, operator='equals')
        return self
    
    def by_text_length(
        self,
        min_length: int = 0,
        max_length: int = float('inf')
    ) -> 'FilteredRetriever':
        """Filter by text length range"""
        self.filter.add_filter(
            'text_length',
            (min_length, max_length),
            operator='range'
        )
        return self
    
    def by_custom(
        self,
        field: str,
        filter_fn: Callable
    ) -> 'FilteredRetriever':
        """Add custom filter function"""
        self.filter.add_filter(
            field,
            custom_fn=filter_fn,
            operator='custom'
        )
        return self
    
    def clear_filters(self) -> 'FilteredRetriever':
        """Clear all filters"""
        self.filter.clear_filters()
        return self
    
    def get_filters_info(self) -> List[Dict]:
        """Get information about active filters"""
        return [
            {
                'field': f['field'],
                'value': f['value'],
                'operator': f['operator']
            }
            for f in self.filter.filters
        ]


# ==========================================================
# UTILITY FUNCTIONS
# ==========================================================

def create_filtered_retriever(base_retriever) -> FilteredRetriever:
    """
    Create filtered retriever wrapper
    
    Args:
        base_retriever: Base SemanticRetriever
        
    Returns:
        FilteredRetriever instance
    """
    return FilteredRetriever(base_retriever)


def demo_filtered_retrieval(
    filtered_retriever: FilteredRetriever,
    query: str = "What are the leave policies?"
):
    """
    Demo filtered retrieval with various filters
    
    Args:
        filtered_retriever: FilteredRetriever instance
        query: Sample query
    """
    print("\n" + "=" * 70)
    print("FILTERED RETRIEVAL DEMO")
    print("=" * 70)
    
    # Demo 1: Basic search
    print(f"\nQuery: {query}")
    print("Filter: None")
    print("-" * 70)
    filtered_retriever.clear_filters()
    results = filtered_retriever.search(query, top_k=2)
    
    for i, result in enumerate(results, 1):
        print(f"Result {i}: {result.get('text', '')[:150]}...")
        print(f"  Score: {result.get('similarity_score', 0):.4f}")
    
    # Demo 2: Filter by category
    print("\n" + "=" * 70)
    print(f"Query: {query}")
    print("Filter: category = 'Compliance'")
    print("-" * 70)
    filtered_retriever.clear_filters()
    filtered_retriever.by_category('Compliance')
    
    results = filtered_retriever.search(query, top_k=2)
    print(f"Results after filtering: {len(results)}")
    
    for i, result in enumerate(results, 1):
        metadata = result.get('metadata', {})
        print(f"Result {i}:")
        print(f"  Category: {metadata.get('category', 'N/A')}")
        print(f"  Score: {result.get('similarity_score', 0):.4f}")
    
    # Demo 3: Multiple filters
    print("\n" + "=" * 70)
    print(f"Query: {query}")
    print("Filters: region = 'Global' AND document_type = 'legal'")
    print("-" * 70)
    filtered_retriever.clear_filters()
    filtered_retriever.by_region('Global').by_document_type('legal')
    
    results = filtered_retriever.search(query, top_k=2)
    print(f"Results after filtering: {len(results)}")


if __name__ == "__main__":
    # Example usage
    from backend.vectorstore.retriever import load_retriever
    
    retriever = load_retriever()
    filtered_retriever = create_filtered_retriever(retriever)
    demo_filtered_retrieval(filtered_retriever)
