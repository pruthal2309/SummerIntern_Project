"""
Groq LLM Service for HR & Compliance RAG System
Handles authentication, prompt submission, token management, and error handling.
"""

import os
import time
import logging
from typing import Dict, Optional, List

from dotenv import load_dotenv
from groq import Groq, APIError, APIConnectionError, RateLimitError

load_dotenv()
logger = logging.getLogger(__name__)


class GroqLLMService:
    """
    LLM service powered by Groq API.
    Sends chat-completion requests with retry logic and structured responses.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.1,
        max_retries: int = 3,
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY", "")
        self.model_name = model_name or os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", str(max_tokens)))
        self.temperature = float(os.getenv("LLM_TEMPERATURE", str(temperature)))
        self.max_retries = max_retries

        if not self.api_key or self.api_key == "your_groq_api_key_here":
            logger.warning("GROQ_API_KEY is not set – LLM calls will fail.")

        self.client = Groq(api_key=self.api_key) if self.api_key else None
        logger.info(
            "GroqLLMService initialised  model=%s  max_tokens=%d  temperature=%.2f",
            self.model_name, self.max_tokens, self.temperature,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
    ) -> Dict:
        """
        Send a chat-completion request to Groq.

        Args:
            messages: List of {"role": ..., "content": ...} dicts.
            max_tokens: Override instance default.
            temperature: Override instance default.

        Returns:
            {
                "answer": str,
                "model": str,
                "usage": {"prompt_tokens": int, "completion_tokens": int, "total_tokens": int},
                "latency_ms": float,
            }
        """
        if self.client is None:
            raise RuntimeError("Groq client is not initialised – set GROQ_API_KEY.")

        effective_max_tokens = max_tokens or self.max_tokens
        effective_temperature = temperature if temperature is not None else self.temperature

        last_error: Optional[Exception] = None

        for attempt in range(1, self.max_retries + 1):
            try:
                start = time.time()
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=effective_max_tokens,
                    temperature=effective_temperature,
                )
                latency_ms = (time.time() - start) * 1000

                choice = response.choices[0]
                usage = response.usage

                result = {
                    "answer": choice.message.content.strip(),
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": usage.prompt_tokens,
                        "completion_tokens": usage.completion_tokens,
                        "total_tokens": usage.total_tokens,
                    },
                    "latency_ms": round(latency_ms, 2),
                }
                logger.info(
                    "LLM response received  tokens=%d  latency=%.0fms",
                    usage.total_tokens, latency_ms,
                )
                return result

            except RateLimitError as exc:
                last_error = exc
                wait = 2 ** attempt
                logger.warning("Rate-limited (attempt %d/%d) – retrying in %ds", attempt, self.max_retries, wait)
                time.sleep(wait)

            except APIConnectionError as exc:
                last_error = exc
                wait = 2 ** attempt
                logger.warning("Connection error (attempt %d/%d) – retrying in %ds", attempt, self.max_retries, wait)
                time.sleep(wait)

            except APIError as exc:
                last_error = exc
                logger.error("Groq API error: %s", exc)
                break  # non-retryable

            except Exception as exc:
                last_error = exc
                logger.error("Unexpected error during LLM call: %s", exc)
                break

        raise RuntimeError(f"LLM generation failed after {self.max_retries} attempts: {last_error}")

    # ------------------------------------------------------------------
    # Health check
    # ------------------------------------------------------------------

    def health_check(self) -> Dict:
        """Return lightweight health status without making an API call."""
        return {
            "available": self.client is not None and bool(self.api_key),
            "model": self.model_name,
            "max_tokens": self.max_tokens,
        }
