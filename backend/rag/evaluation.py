"""
RAG Evaluation Utilities for HR & Compliance System
Measures answer relevance, context grounding, response latency, and edge-case handling.
"""

import time
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ======================================================================
# SAMPLE TEST QUERIES
# ======================================================================

SAMPLE_QUERIES = [
    {
        "question": "What is the maternity leave policy?",
        "expected_behaviour": "Should return information about maternity/parental leave from HR documents.",
    },
    {
        "question": "What are the compliance requirements for data protection?",
        "expected_behaviour": "Should cite data-protection or GDPR-related policies.",
    },
    {
        "question": "How do I file a grievance?",
        "expected_behaviour": "Should describe the grievance procedure with steps.",
    },
    {
        "question": "What is the employee compensation structure?",
        "expected_behaviour": "Should reference pay-grade / compensation policies.",
    },
    {
        "question": "Tell me about the remote work policy.",
        "expected_behaviour": "Should outline WFH / remote work guidelines.",
    },
    {
        "question": "What is the meaning of life?",
        "expected_behaviour": "Should indicate that the information is not in the provided documents.",
    },
]


class RAGEvaluator:
    """
    Evaluate the full RAG pipeline on relevance, grounding, and latency.
    """

    def __init__(self, pipeline):
        """
        Args:
            pipeline: An initialised RAGPipeline instance.
        """
        self.pipeline = pipeline

    # ------------------------------------------------------------------
    # Latency evaluation
    # ------------------------------------------------------------------

    def measure_latency(
        self,
        question: str,
        top_k: int = 5,
        iterations: int = 1,
    ) -> Dict:
        """
        Measure end-to-end latency for a single query.

        Returns:
            Dict with mean/min/max latency in milliseconds.
        """
        times: List[float] = []

        for _ in range(iterations):
            start = time.time()
            self.pipeline.answer(question, top_k=top_k)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

        return {
            "question": question,
            "iterations": iterations,
            "mean_ms": round(sum(times) / len(times), 2),
            "min_ms": round(min(times), 2),
            "max_ms": round(max(times), 2),
        }

    # ------------------------------------------------------------------
    # Grounding check
    # ------------------------------------------------------------------

    @staticmethod
    def check_grounding(response: Dict) -> Dict:
        """
        Heuristic check: does the answer reference the retrieved sources?

        Args:
            response: Output of RAGPipeline.answer().

        Returns:
            Grounding report dict.
        """
        answer = response.get("answer", "")
        sources = response.get("sources", [])
        doc_ids = [s.get("doc_id", "") for s in sources]

        # Simple heuristic: see how many source doc_ids appear in the answer text
        cited = [did for did in doc_ids if did and did in answer]

        no_info_phrases = [
            "could not find",
            "not available",
            "no relevant",
            "insufficient information",
        ]
        is_refusal = any(phrase in answer.lower() for phrase in no_info_phrases)

        return {
            "total_sources": len(doc_ids),
            "cited_in_answer": len(cited),
            "is_refusal": is_refusal,
            "grounded": len(cited) > 0 or is_refusal,
        }

    # ------------------------------------------------------------------
    # Batch evaluation
    # ------------------------------------------------------------------

    def evaluate_batch(
        self,
        queries: Optional[List[Dict]] = None,
        top_k: int = 5,
    ) -> Dict:
        """
        Run a batch of test queries and collect evaluation metrics.

        Args:
            queries: List of {"question": str, "expected_behaviour": str}.
                     Defaults to SAMPLE_QUERIES.
            top_k: Number of documents to retrieve.

        Returns:
            Evaluation report dict.
        """
        queries = queries or SAMPLE_QUERIES
        results: List[Dict] = []

        for q in queries:
            question = q["question"]
            expected = q.get("expected_behaviour", "")

            try:
                start = time.time()
                response = self.pipeline.answer(question, top_k=top_k)
                elapsed_ms = (time.time() - start) * 1000

                grounding = self.check_grounding(response)
                results.append({
                    "question": question,
                    "expected_behaviour": expected,
                    "answer_preview": response["answer"][:300],
                    "num_sources": len(response.get("sources", [])),
                    "grounding": grounding,
                    "latency_ms": round(elapsed_ms, 2),
                    "success": True,
                })
            except Exception as exc:
                logger.error("Evaluation failed for '%s': %s", question[:60], exc)
                results.append({
                    "question": question,
                    "success": False,
                    "error": str(exc),
                })

        # Aggregate
        successes = [r for r in results if r.get("success")]
        latencies = [r["latency_ms"] for r in successes]
        grounded_count = sum(1 for r in successes if r.get("grounding", {}).get("grounded"))

        report = {
            "total_queries": len(queries),
            "successful": len(successes),
            "failed": len(queries) - len(successes),
            "grounded_fraction": grounded_count / len(successes) if successes else 0,
            "avg_latency_ms": round(sum(latencies) / len(latencies), 2) if latencies else 0,
            "max_latency_ms": round(max(latencies), 2) if latencies else 0,
            "details": results,
        }

        return report

    # ------------------------------------------------------------------
    # Edge-case tests
    # ------------------------------------------------------------------

    def test_edge_cases(self) -> List[Dict]:
        """
        Run edge-case scenarios and return results.
        """
        cases: List[Dict] = []

        # 1. Empty query
        try:
            resp = self.pipeline.answer("")
            cases.append({
                "case": "empty_query",
                "passed": "provide" in resp["answer"].lower() or "empty" in resp["answer"].lower(),
                "answer_preview": resp["answer"][:200],
            })
        except Exception as exc:
            cases.append({"case": "empty_query", "passed": False, "error": str(exc)})

        # 2. Off-topic query (should refuse)
        try:
            resp = self.pipeline.answer("What is the weather in Tokyo right now?")
            grounding = self.check_grounding(resp)
            cases.append({
                "case": "off_topic_query",
                "passed": grounding["is_refusal"] or grounding["grounded"],
                "answer_preview": resp["answer"][:200],
            })
        except Exception as exc:
            cases.append({"case": "off_topic_query", "passed": False, "error": str(exc)})

        # 3. Very long query
        try:
            long_q = "What is the leave policy? " * 100
            resp = self.pipeline.answer(long_q)
            cases.append({
                "case": "very_long_query",
                "passed": bool(resp.get("answer")),
                "answer_preview": resp["answer"][:200],
            })
        except Exception as exc:
            cases.append({"case": "very_long_query", "passed": False, "error": str(exc)})

        return cases


# ======================================================================
# CLI helper
# ======================================================================

def run_evaluation():
    """Quick CLI evaluation runner."""
    from backend.rag.rag_pipeline import RAGPipeline

    logging.basicConfig(level=logging.INFO)

    print("=" * 70)
    print("RAG PIPELINE EVALUATION")
    print("=" * 70)

    pipeline = RAGPipeline()
    evaluator = RAGEvaluator(pipeline)

    # Batch evaluation
    print("\n--- Batch Evaluation ---")
    report = evaluator.evaluate_batch()
    print(f"Total: {report['total_queries']}  "
          f"Success: {report['successful']}  "
          f"Grounded: {report['grounded_fraction']:.0%}  "
          f"Avg Latency: {report['avg_latency_ms']:.0f}ms")

    for detail in report["details"]:
        status = "✓" if detail.get("success") else "✗"
        print(f"  {status} {detail['question'][:60]}")

    # Edge cases
    print("\n--- Edge-case Tests ---")
    edge_results = evaluator.test_edge_cases()
    for case in edge_results:
        status = "✓" if case.get("passed") else "✗"
        print(f"  {status} {case['case']}")

    print("\nDone.")


if __name__ == "__main__":
    run_evaluation()
