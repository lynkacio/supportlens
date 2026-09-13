"""LLM analysis service.

Responsibilities: turn a raw customer message into a validated TicketAnalysis.
This module does not touch the database or HTTP — it is a pure function boundary.

Provider: DeepSeek (OpenAI-compatible protocol, base_url points at DeepSeek).

IMPORTANT: DeepSeek's chat completions only supports `json_object`, which guarantees
valid JSON but NOT schema compliance. Enum validity therefore depends entirely on the
Pydantic validation + self-correction retry implemented in this module.
"""

from __future__ import annotations

import logging
import time

from openai import (
    APIConnectionError,
    APIError,
    APITimeoutError,
    OpenAI,
    RateLimitError,
)
from pydantic import BaseModel, Field, ValidationError

from app.config import get_deepseek_api_key
from app.enums import Category, Priority

logger = logging.getLogger(__name__)

BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-chat"          # ← 用 models.list() 实测后确认/修改
MAX_ATTEMPTS = 3
BASE_BACKOFF_SECONDS = 1.0


class LLMServiceError(Exception):
    """Raised when the LLM cannot produce a valid analysis result."""


class TicketAnalysis(BaseModel):
    """LLM output contract. Enums enforced here — invalid values cannot reach the next layer."""

    category: Category
    priority: Priority
    summary: str = Field(min_length=1, max_length=500)
    suggested_response: str = Field(min_length=1, max_length=2000)


SYSTEM_PROMPT = """You are a support ticket classification assistant. Analyze the customer message and return a single JSON object.

The JSON object must contain exactly these four keys:
- "category": one of billing | technical | account | feature_request | other
- "priority": one of low | medium | high | urgent
- "summary": one sentence, neutral and factual
- "suggested_response": a polite reply to the customer

category rules:
- billing: billing, refunds, invoices, payment issues
- technical: bugs, errors, outages, broken functionality
- account: login, password, permissions, profile, security settings
- feature_request: requests for new features
- other: none of the above clearly applies

priority rules (strict):
- urgent: service outage, security incident, data loss, or revenue completely blocked
- high: core functionality broken with no workaround, or the customer is clearly very angry
- medium: functionality impaired but a workaround exists
- low: inquiries, cosmetic issues, feature suggestions

Output JSON only. Do not include any explanatory text."""


_client: OpenAI | None = None


def _get_client() -> OpenAI:
    """Create the client lazily — importing this module will not fail due to a missing key."""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=get_deepseek_api_key(),
            base_url=BASE_URL,
        )
    return _client


def analyze_ticket(
    customer_message: str,
    client: OpenAI | None = None,
) -> TicketAnalysis:
    """Analyze a single customer message.

    The `client` parameter is used for test injection; leave it empty for production calls.
    """
    if not customer_message or not customer_message.strip():
        raise LLMServiceError("customer_message is empty")

    client = client or _get_client()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": customer_message},
    ]

    last_error: Exception | None = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0,
            )
        except (APITimeoutError, APIConnectionError, RateLimitError) as exc:
            last_error = exc
            logger.warning(
                "LLM transient error (attempt %d/%d): %s", attempt, MAX_ATTEMPTS, exc
            )
            if attempt < MAX_ATTEMPTS:
                time.sleep(BASE_BACKOFF_SECONDS * attempt)
            continue
        except APIError as exc:
            logger.exception("Non-retryable LLM API error")
            raise LLMServiceError(f"LLM API error: {exc}") from exc

        raw = completion.choices[0].message.content or ""

        try:
            return TicketAnalysis.model_validate_json(raw)   # ← hard gate
        except ValidationError as exc:
            last_error = exc
            logger.warning(
                "Invalid LLM payload (attempt %d/%d): %s", attempt, MAX_ATTEMPTS, exc
            )
            if attempt < MAX_ATTEMPTS:
                # Feed the bad output and the reason back, so the model can self-correct.
                messages.append({"role": "assistant", "content": raw})
                messages.append({
                    "role": "user",
                    "content": (
                        f"Your previous output was invalid: {exc}. "
                        "Return corrected JSON only. "
                        "category must be one of: billing, technical, account, "
                        "feature_request, other. "
                        "priority must be one of: low, medium, high, urgent."
                    ),
                })

    raise LLMServiceError(
        f"LLM analysis still failed after {MAX_ATTEMPTS} attempts"
    ) from last_error