"""
Prompt Builder for HR & Compliance RAG System
Constructs structured prompts with system instructions, context, and response constraints.
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ======================================================================
# DEFAULT TEMPLATES
# ======================================================================

SYSTEM_TEMPLATE = (
    "You are an **HR & Compliance Assistant** for an enterprise organisation.\n\n"
    "## Rules\n"
    "1. Answer the user's question **only** using the context provided below.\n"
    "2. If the context does not contain enough information, respond with: "
    "\"I'm sorry, I could not find sufficient information in the available documents "
    "to answer your question.\"\n"
    "3. Do **not** make up policies, numbers, or procedures that are not explicitly "
    "stated in the context.\n"
    "4. When possible, **cite the source document** (e.g. document ID or filename) "
    "for each piece of information you reference.\n"
    "5. Keep your answer concise, accurate, and well-organised.\n"
    "6. If the question is ambiguous, state the ambiguity and answer based on the "
    "most reasonable interpretation.\n"
)

USER_TEMPLATE = (
    "## Context (retrieved documents)\n"
    "{context_block}\n\n"
    "## Question\n"
    "{question}\n\n"
    "## Instructions\n"
    "Answer the question above using **only** the context provided. "
    "Cite the source document for each claim. "
    "If the information is not available, say so clearly."
)


class PromptBuilder:
    """
    Builds structured prompt messages for the LLM from retrieved chunks.
    """

    def __init__(
        self,
        system_template: Optional[str] = None,
        user_template: Optional[str] = None,
        max_context_chars: int = 12_000,
    ):
        """
        Args:
            system_template: Override the default system message.
            user_template: Override the default user message template.
            max_context_chars: Hard cap on total context length to avoid token overflow.
        """
        self.system_template = system_template or SYSTEM_TEMPLATE
        self.user_template = user_template or USER_TEMPLATE
        self.max_context_chars = max_context_chars

    # ------------------------------------------------------------------
    # Context formatting
    # ------------------------------------------------------------------

    def format_context(self, chunks: List[Dict]) -> str:
        """
        Format a list of retrieved chunks into a numbered context block.

        Each chunk is expected to have:
            - text: str
            - metadata: dict (optional but recommended)
            - similarity_score: float (optional)

        Returns:
            Formatted context string.
        """
        if not chunks:
            return "(No documents were retrieved.)"

        blocks: List[str] = []
        total_chars = 0

        for idx, chunk in enumerate(chunks, 1):
            text = chunk.get("text", "").strip()
            metadata = chunk.get("metadata", {})
            score = chunk.get("similarity_score")

            # Build header line
            source = metadata.get("source", "unknown")
            doc_id = metadata.get("doc_id", "N/A")
            category = metadata.get("category", "")
            header_parts = [f"**[Document {idx}]**  source: {source}  |  doc_id: {doc_id}"]
            if category:
                header_parts.append(f"category: {category}")
            if score is not None:
                header_parts.append(f"relevance: {score:.4f}")
            header = "  |  ".join(header_parts)

            block = f"{header}\n{text}"

            # Respect context budget
            if total_chars + len(block) > self.max_context_chars:
                remaining = self.max_context_chars - total_chars
                if remaining > 200:  # still useful
                    block = block[:remaining] + "\n... [truncated]"
                    blocks.append(block)
                break

            blocks.append(block)
            total_chars += len(block)

        return "\n\n---\n\n".join(blocks)

    # ------------------------------------------------------------------
    # Message building
    # ------------------------------------------------------------------

    def build_messages(
        self,
        question: str,
        chunks: List[Dict],
    ) -> List[Dict[str, str]]:
        """
        Build the final list of messages to send to the LLM.

        Args:
            question: User's question.
            chunks: Retrieved document chunks.

        Returns:
            List of {"role": ..., "content": ...} dicts.
        """
        context_block = self.format_context(chunks)

        user_content = self.user_template.format(
            context_block=context_block,
            question=question,
        )

        messages = [
            {"role": "system", "content": self.system_template},
            {"role": "user", "content": user_content},
        ]

        logger.debug(
            "Prompt built  context_chars=%d  chunks=%d",
            len(context_block), len(chunks),
        )
        return messages
