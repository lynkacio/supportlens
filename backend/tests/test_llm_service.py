"""Tests for the LLM analysis service, using a fake client.

These tests exercise the validation + retry logic in `analyze_ticket`
without making any real API calls, so they are fast, deterministic, and free.
"""

import json
from types import SimpleNamespace

import pytest

from app.services.llm_service import LLMServiceError, TicketAnalysis, analyze_ticket, answer_question


# ─────────────────────────────────────────────────────────────
# Fake client: simulates the OpenAI-compatible chat.completions interface
# by returning a preset sequence of response strings.
# ─────────────────────────────────────────────────────────────
class FakeChatCompletions:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        content = self.responses[self.calls - 1]
        return SimpleNamespace(
            choices=[
                SimpleNamespace(
                    message=SimpleNamespace(content=content)
                )
            ]
        )


class FakeChat:
    def __init__(self, responses):
        self.completions = FakeChatCompletions(responses)


class FakeClient:
    def __init__(self, responses):
        self.chat = FakeChat(responses)


def _valid_json():
    return json.dumps({
        "category": "billing",
        "priority": "high",
        "summary": "Customer was charged twice.",
        "suggested_response": "We are sorry and will refund the duplicate.",
    })


def _invalid_enum_json():
    # category is not in the allowed enum → ValidationError
    return json.dumps({
        "category": "billing_issue",
        "priority": "high",
        "summary": "Customer was charged twice.",
        "suggested_response": "We are sorry and will refund the duplicate.",
    })


# ─────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────
def test_valid_json_returns_ticket_analysis():
    client = FakeClient([_valid_json()])

    result = analyze_ticket("I was charged twice this month.", client=client)

    assert isinstance(result, TicketAnalysis)
    assert result.category == "billing"
    assert result.priority == "high"
    assert client.chat.completions.calls == 1


def test_invalid_enum_triggers_retries_and_finally_fails():
    # All retries return invalid JSON → LLMServiceError after MAX_ATTEMPTS
    client = FakeClient([_invalid_enum_json()] * 3)

    with pytest.raises(LLMServiceError):
        analyze_ticket("I was charged twice this month.", client=client)

    assert client.chat.completions.calls == 3


def test_invalid_then_valid_corrects_on_second_attempt():
    client = FakeClient([_invalid_enum_json(), _valid_json()])

    result = analyze_ticket("I was charged twice this month.", client=client)

    assert isinstance(result, TicketAnalysis)
    assert result.category == "billing"
    assert client.chat.completions.calls == 2


def test_empty_message_raises_immediately():
    with pytest.raises(LLMServiceError):
        analyze_ticket("", client=FakeClient([_valid_json()]))
        

def test_answer_question_returns_text():
    client = FakeClient(["The most recent high-priority issue is ticket #100."])

    result = answer_question(
        "What is the most recent high-priority issue?",
        "- [100] urgent: Login is failing",
        client=client,
    )

    assert "ticket #100" in result