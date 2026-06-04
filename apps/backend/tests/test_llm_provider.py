from __future__ import annotations

import pytest
from pydantic import BaseModel

from src.core.config import settings
from src.infrastructure.ai.providers.mock_provider import MockLLMProvider
from src.infrastructure.ai.providers.openai_compatible import OpenAICompatibleProvider


class _TestSchema(BaseModel):
    name: str
    score: float
    tags: list[str]
    metadata: dict[str, str]


class TestOpenAICompatibleProvider:
    @pytest.mark.skipif(not settings.LLM_API_KEY, reason="LLM_API_KEY not configured")
    async def test_generate_returns_string(self) -> None:
        provider = OpenAICompatibleProvider(temperature=0.0)
        messages = [{"role": "user", "content": "Say 'hello' in exactly one word."}]
        result = await provider.generate(messages)
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.skipif(not settings.LLM_API_KEY, reason="LLM_API_KEY not configured")
    async def test_generate_structured_returns_valid_object(self) -> None:
        provider = OpenAICompatibleProvider(temperature=0.0)
        result = await provider.generate_structured(
            [
                {
                    "role": "user",
                    "content": "Return JSON: name=test, score=0.95, tags=['a','b'], metadata={}",
                }
            ],
            _TestSchema,
        )
        assert isinstance(result, _TestSchema)
        assert isinstance(result.name, str)
        assert isinstance(result.score, float)
        assert isinstance(result.tags, list)

    async def test_mock_provider_works(self) -> None:
        provider = MockLLMProvider()
        result = await provider.generate_structured(
            [{"role": "user", "content": "any text"}],
            _TestSchema,
        )
        assert isinstance(result, _TestSchema)


class TestMockLLMProvider:
    async def test_text_response_keyword_match(self) -> None:
        provider = MockLLMProvider(text_responses={"hello": "world"})
        result = await provider.generate([{"role": "user", "content": "hello there"}])
        assert result == "world"

    async def test_text_response_fallback(self) -> None:
        provider = MockLLMProvider(default_response="fallback")
        result = await provider.generate([{"role": "user", "content": "unmatched text"}])
        assert result == "fallback"

    async def test_text_response_case_insensitive(self) -> None:
        provider = MockLLMProvider(text_responses={"ERROR": "fail"})
        result = await provider.generate([{"role": "user", "content": "an error occurred"}])
        assert result == "fail"

    async def test_structured_fixture_match(self) -> None:
        fixture = _TestSchema(name="test", score=1.0, tags=["a"], metadata={})
        provider = MockLLMProvider(structured_fixtures={"hello": fixture})
        result = await provider.generate_structured(
            [{"role": "user", "content": "hello world"}],
            _TestSchema,
        )
        assert result == fixture
        assert result.name == "test"
        assert result.score == 1.0

    async def test_structured_auto_construct(self) -> None:
        provider = MockLLMProvider()
        result = await provider.generate_structured(
            [{"role": "user", "content": "no fixture matches this"}],
            _TestSchema,
        )
        assert isinstance(result, _TestSchema)
        assert result.name == ""
        assert result.score == 0.5
        assert result.tags == []
        assert result.metadata == {}

    async def test_call_log_records_text_generate(self) -> None:
        provider = MockLLMProvider(text_responses={"ping": "pong"})
        await provider.generate([{"role": "user", "content": "ping"}])
        assert len(provider.call_log) == 1
        entry = provider.call_log[0]
        assert entry["method"] == "generate"
        assert entry["response"] == "pong"

    async def test_call_log_records_structured_generate(self) -> None:
        provider = MockLLMProvider()
        await provider.generate_structured(
            [{"role": "user", "content": "test"}],
            _TestSchema,
        )
        assert len(provider.call_log) == 1
        entry = provider.call_log[0]
        assert entry["method"] == "generate_structured"
        assert entry["schema"] == "_TestSchema"
        assert isinstance(entry["response"], _TestSchema)

    async def test_reset_log(self) -> None:
        provider = MockLLMProvider()
        await provider.generate([{"role": "user", "content": "test"}])
        assert len(provider.call_log) == 1
        provider.reset_log()
        assert len(provider.call_log) == 0
