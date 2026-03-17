"""
Retrieval Evaluation Module for HR & Compliance RAG System
Measures retrieval quality, accuracy, and performance
"""

import json
import time
import numpy as np
from typing import List, Dict, Tuple, Optional
from collections import defaultdict


# ==========================================================
# EVALUATION METRICS
# ==========================================================

class RetrievalEvaluator:
    """
    Evaluates retrieval quality and performance
    Measures accuracy, relevance, and latency metrics
    """
    
    def __init__(self, retriever):
        """
        Initialize evaluator
        
        Args:
            retriever: SemanticRetriever instance
        """
        self.retriever = retriever
        self.results = {
            'metrics': {},
            'timings': [],
            'relevance_scores': [],
            'failed_queries': []
        }
    
    # ==========================================================
    # RANKING METRICS
    # ==========================================================
    
    def calculate_mrr(
        self,
        query: str,
        relevant_docs: List[str],
        top_k: int = 5
    ) -> float:
        """
        Calculate Mean Reciprocal Rank (MRR)
        Position of first relevant document
        
        Args:
            query: Query text
            relevant_docs: List of relevant document IDs
            top_k: Number of results to consider
            
        Returns:
            MRR score (1.0 = perfect, 0.0 = no relevant docs)
        """
        results = self.retriever.search(query, top_k=top_k)
        
        for rank, result in enumerate(results, 1):
            doc_id = result.get('metadata', {}).get('doc_id')
            if doc_id in relevant_docs:
                return 1.0 / rank
        
        return 0.0
    
    def calculate_precision_at_k(
        self,
        query: str,
        relevant_docs: List[str],
        k: int = 5
    ) -> float:
        """
        Calculate Precision@K
        Fraction of top-k results that are relevant
        
        Args:
            query: Query text
            relevant_docs: List of relevant document IDs
            k: Cutoff rank
            
        Returns:
            Precision@K (0.0 to 1.0)
        """
        results = self.retriever.search(query, top_k=k)
        
        if not results:
            return 0.0
        
        relevant_count = 0
        for result in results[:k]:
            doc_id = result.get('metadata', {}).get('doc_id')
            if doc_id in relevant_docs:
                relevant_count += 1
        
        return relevant_count / min(k, len(results))
    
    def calculate_recall_at_k(
        self,
        query: str,
        relevant_docs: List[str],
        k: int = 5
    ) -> float:
        """
        Calculate Recall@K
        Fraction of relevant documents retrieved in top-k
        
        Args:
            query: Query text
            relevant_docs: List of relevant document IDs
            k: Cutoff rank
            
        Returns:
            Recall@K (0.0 to 1.0)
        """
        if not relevant_docs:
            return 1.0  # Vacuous truth
        
        results = self.retriever.search(query, top_k=k)
        
        relevant_count = 0
        for result in results[:k]:
            doc_id = result.get('metadata', {}).get('doc_id')
            if doc_id in relevant_docs:
                relevant_count += 1
        
        return relevant_count / len(relevant_docs)
    
    def calculate_ndcg_at_k(
        self,
        query: str,
        relevant_docs: List[str],
        k: int = 5,
        relevance_scores: Optional[Dict[str, float]] = None
    ) -> float:
        """
        Calculate Normalized Discounted Cumulative Gain (NDCG@K)
        Considers both ranking position and relevance
        
        Args:
            query: Query text
            relevant_docs: List of relevant document IDs or dict with scores
            k: Cutoff rank
            relevance_scores: Optional dict of doc_id -> relevance_score
            
        Returns:
            NDCG@K (0.0 to 1.0)
        """
        results = self.retriever.search(query, top_k=k)
        
        # Prepare relevance dict
        if isinstance(relevant_docs, dict):
            relevance = relevant_docs
        else:
            relevance = {doc_id: 1.0 for doc_id in relevant_docs}
        
        # Calculate DCG
        dcg = 0.0
        for rank, result in enumerate(results[:k], 1):
            doc_id = result.get('metadata', {}).get('doc_id')
            relevance_score = relevance.get(doc_id, 0.0)
            dcg += relevance_score / np.log2(rank + 1)
        
        # Calculate IDCG (ideal ranking)
        sorted_relevances = sorted(relevance.values(), reverse=True)[:k]
        idcg = sum(
            score / np.log2(rank + 1)
            for rank, score in enumerate(sorted_relevances, 1)
        )
        
        if idcg == 0:
            return 0.0
        
        return dcg / idcg
    
    # ==========================================================
    # RELEVANCE METRICS
    # ==========================================================
    
    def evaluate_result_relevance(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict:
        """
        Evaluate relevance of retrieval results
        
        Args:
            query: Query text
            top_k: Number of results
            
        Returns:
            Relevance evaluation report
        """
        results = self.retriever.search(query, top_k=top_k)
        
        report = {
            'query': query,
            'num_results': len(results),
            'scores': [],
            'avg_score': 0.0,
            'score_distribution': {}
        }
        
        scores = []
        for result in results:
            score = result.get('similarity_score', 0.0)
            scores.append(score)
            
            # Score bucketing for distribution
            bucket = int(score * 10) / 10
            report['score_distribution'][bucket] = \
                report['score_distribution'].get(bucket, 0) + 1
        
        report['scores'] = scores
        report['avg_score'] = np.mean(scores) if scores else 0.0
        report['max_score'] = np.max(scores) if scores else 0.0
        report['min_score'] = np.min(scores) if scores else 0.0
        report['std_score'] = np.std(scores) if scores else 0.0
        
        return report
    
    # ==========================================================
    # PERFORMANCE METRICS
    # ==========================================================
    
    def measure_latency(
        self,
        query: str,
        top_k: int = 5,
        iterations: int = 1
    ) -> Dict:
        """
        Measure query latency
        
        Args:
            query: Query text
            top_k: Number of results
            iterations: Number of times to run
            
        Returns:
            Latency statistics
        """
        times = []
        
        for _ in range(iterations):
            start = time.time()
            self.retriever.search(query, top_k=top_k)
            elapsed = (time.time() - start) * 1000  # Convert to ms
            times.append(elapsed)
        
        return {
            'query': query,
            'mean_ms': np.mean(times),
            'median_ms': np.median(times),
            'min_ms': np.min(times),
            'max_ms': np.max(times),
            'std_ms': np.std(times),
            'p95_ms': np.percentile(times, 95),
            'p99_ms': np.percentile(times, 99)
        }
    
    def benchmark_throughput(
        self,
        queries: List[str],
        top_k: int = 5
    ) -> Dict:
        """
        Benchmark query throughput
        
        Args:
            queries: List of queries
            top_k: Number of results
            
        Returns:
            Throughput statistics
        """
        start = time.time()
        total_queries = 0
        
        for query in queries:
            self.retriever.search(query, top_k=top_k)
            total_queries += 1
        
        total_time = time.time() - start
        
        return {
            'total_queries': total_queries,
            'total_time_s': total_time,
            'queries_per_second': total_queries / total_time if total_time > 0 else 0,
            'avg_time_per_query_ms': (total_time / total_queries * 1000) if total_queries > 0 else 0
        }
    
    # ==========================================================
    # BATCH EVALUATION
    # ==========================================================
    
    def evaluate_queries(
        self,
        test_set: List[Dict],
        top_k: int = 5
    ) -> Dict:
        """
        Evaluate entire set of queries
        
        Args:
            test_set: List of queries with relevant_docs
                [{
                    'query': 'text',
                    'relevant_docs': ['doc_id1', 'doc_id2']
                }, ...]
            top_k: Number of results
            
        Returns:
            Comprehensive evaluation results
        """
        mrr_scores = []
        precision_scores = []
        recall_scores = []
        ndcg_scores = []
        latencies = []
        
        for item in test_set:
            query = item['query']
            relevant_docs = item['relevant_docs']
            
            try:
                # Calculate metrics
                mrr = self.calculate_mrr(query, relevant_docs, top_k)
                precision = self.calculate_precision_at_k(query, relevant_docs, top_k)
                recall = self.calculate_recall_at_k(query, relevant_docs, top_k)
                ndcg = self.calculate_ndcg_at_k(query, relevant_docs, top_k)
                
                mrr_scores.append(mrr)
                precision_scores.append(precision)
                recall_scores.append(recall)
                ndcg_scores.append(ndcg)
                
                # Measure latency
                latency_result = self.measure_latency(query, top_k=top_k, iterations=1)
                latencies.append(latency_result['mean_ms'])
                
            except Exception as e:
                print(f"Error evaluating query '{query}': {e}")
                self.results['failed_queries'].append({
                    'query': query,
                    'error': str(e)
                })
        
        # Aggregate results
        evaluation_report = {
            'num_queries': len(test_set),
            'successful_queries': len(mrr_scores),
            'failed_queries': len(test_set) - len(mrr_scores),
            'metrics': {
                'mrr': {
                    'mean': np.mean(mrr_scores) if mrr_scores else 0.0,
                    'median': np.median(mrr_scores) if mrr_scores else 0.0,
                    'min': np.min(mrr_scores) if mrr_scores else 0.0,
                    'max': np.max(mrr_scores) if mrr_scores else 0.0,
                    'std': np.std(mrr_scores) if mrr_scores else 0.0
                },
                'precision': {
                    'mean': np.mean(precision_scores) if precision_scores else 0.0,
                    'median': np.median(precision_scores) if precision_scores else 0.0,
                    'min': np.min(precision_scores) if precision_scores else 0.0,
                    'max': np.max(precision_scores) if precision_scores else 0.0,
                    'std': np.std(precision_scores) if precision_scores else 0.0
                },
                'recall': {
                    'mean': np.mean(recall_scores) if recall_scores else 0.0,
                    'median': np.median(recall_scores) if recall_scores else 0.0,
                    'min': np.min(recall_scores) if recall_scores else 0.0,
                    'max': np.max(recall_scores) if recall_scores else 0.0,
                    'std': np.std(recall_scores) if recall_scores else 0.0
                },
                'ndcg': {
                    'mean': np.mean(ndcg_scores) if ndcg_scores else 0.0,
                    'median': np.median(ndcg_scores) if ndcg_scores else 0.0,
                    'min': np.min(ndcg_scores) if ndcg_scores else 0.0,
                    'max': np.max(ndcg_scores) if ndcg_scores else 0.0,
                    'std': np.std(ndcg_scores) if ndcg_scores else 0.0
                }
            },
            'latency': {
                'mean_ms': np.mean(latencies) if latencies else 0.0,
                'median_ms': np.median(latencies) if latencies else 0.0,
                'p95_ms': np.percentile(latencies, 95) if latencies else 0.0,
                'p99_ms': np.percentile(latencies, 99) if latencies else 0.0
            }
        }
        
        return evaluation_report
    
    # ==========================================================
    # REPORTING
    # ==========================================================
    
    def generate_report(self, output_path: str = "data/processed/evaluation_report.json"):
        """
        Generate and save evaluation report
        
        Args:
            output_path: Path to save report
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"Evaluation report saved to: {output_path}")
    
    def print_summary(self, evaluation_result: Dict):
        """
        Print evaluation summary
        
        Args:
            evaluation_result: Evaluation result from evaluate_queries
        """
        print("\n" + "=" * 70)
        print("RETRIEVAL EVALUATION SUMMARY")
        print("=" * 70)
        
        print(f"\nQueries Evaluated: {evaluation_result['num_queries']}")
        print(f"Successful: {evaluation_result['successful_queries']}")
        print(f"Failed: {evaluation_result['failed_queries']}")
        
        print("\n" + "-" * 70)
        print("METRICS")
        print("-" * 70)
        
        metrics = evaluation_result['metrics']
        
        for metric_name, stats in metrics.items():
            print(f"\n{metric_name.upper()}:")
            print(f"  Mean:   {stats['mean']:.4f}")
            print(f"  Median: {stats['median']:.4f}")
            print(f"  Min:    {stats['min']:.4f}")
            print(f"  Max:    {stats['max']:.4f}")
            print(f"  Std:    {stats['std']:.4f}")
        
        print("\n" + "-" * 70)
        print("LATENCY")
        print("-" * 70)
        
        latency = evaluation_result['latency']
        print(f"\nMean Latency:   {latency['mean_ms']:.2f} ms")
        print(f"Median Latency: {latency['median_ms']:.2f} ms")
        print(f"P95 Latency:    {latency['p95_ms']:.2f} ms")
        print(f"P99 Latency:    {latency['p99_ms']:.2f} ms")


# ==========================================================
# SAMPLE TEST SET
# ==========================================================

def get_sample_test_set() -> List[Dict]:
    """
    Get sample test queries for evaluation
    
    Returns:
        List of test queries with relevant documents
    """
    return [
        {
            'query': 'What are the employee leave policies?',
            'relevant_docs': []  # Empty for now - user should populate
        },
        {
            'query': 'Tell me about compliance requirements',
            'relevant_docs': []
        },
        {
            'query': 'What is the grievance procedure?',
            'relevant_docs': []
        },
        {
            'query': 'Employee compensation structure',
            'relevant_docs': []
        },
        {
            'query': 'Remote work policy guidelines',
            'relevant_docs': []
        }
    ]


def demo_evaluation(retriever, test_set: Optional[List[Dict]] = None):
    """
    Demo evaluation of retriever
    
    Args:
        retriever: SemanticRetriever instance
        test_set: Optional test set of queries
    """
    if test_set is None:
        test_set = get_sample_test_set()
    
    evaluator = RetrievalEvaluator(retriever)
    
    print("\n" + "=" * 70)
    print("RETRIEVAL EVALUATION DEMO")
    print("=" * 70)
    
    # Measure latency on first query
    if test_set:
        query = test_set[0]['query']
        print(f"\nLatency Test Query: {query}")
        latency_result = evaluator.measure_latency(query, top_k=5, iterations=5)
        print(f"  Mean: {latency_result['mean_ms']:.2f} ms")
        print(f"  P99: {latency_result['p99_ms']:.2f} ms")
    
    # Evaluate result relevance
    if test_set:
        query = test_set[0]['query']
        print(f"\nRelevance Test Query: {query}")
        relevance_result = evaluator.evaluate_result_relevance(query, top_k=3)
        print(f"  Avg Score: {relevance_result['avg_score']:.4f}")
        print(f"  Score Std: {relevance_result['std_score']:.4f}")


if __name__ == "__main__":
    from backend.vectorstore.retriever import load_retriever
    
    retriever = load_retriever()
    demo_evaluation(retriever)
