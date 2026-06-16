from typing import Any, TypeVar

from langchain_core.runnables import Runnable, RunnableLambda
from pydantic import BaseModel

from src.domain.ai.provider import LLMProviderPort

T = TypeVar("T", bound=BaseModel)


class MockLLMProvider(LLMProviderPort):
    """Testing mock provider — zero network, zero cost.

    Keyword matching on concatenated user message content against
    pre-configured response fixtures. Records all calls for assertions.
    """

    def __init__(
        self,
        text_responses: dict[str, str] | None = None,
        structured_fixtures: dict[str, Any] | None = None,
        default_response: str = "mock response",
    ) -> None:
        self.text_responses = text_responses or {}
        self.structured_fixtures = structured_fixtures or {}
        self.default_response = default_response
        self.call_log: list[dict[str, Any]] = []

    def _match_fixture_key(
        self, messages: list[dict[str, str]], pool: dict[str, Any]
    ) -> str | None:
        """Return the first pool key whose keyword appears in user messages."""
        user_text = " ".join(m["content"] for m in messages if m.get("role") == "user").lower()
        for keyword in pool:
            if keyword.lower() in user_text:
                return keyword
        return None

    async def generate(self, messages: list[dict[str, str]]) -> str:
        key = self._match_fixture_key(messages, self.text_responses)
        response = self.text_responses[key] if key else self.default_response
        self.call_log.append({"method": "generate", "messages": messages, "response": response})
        return response

    async def generate_structured(
        self, messages: list[dict[str, str]], output_schema: type[T]
    ) -> T:
        key = self._match_fixture_key(messages, self.structured_fixtures)
        if key:
            result = self.structured_fixtures[key]
        else:
            result = output_schema(
                **{
                    field: self._default_for(field_info.annotation)
                    for field, field_info in output_schema.model_fields.items()
                }
            )
        self.call_log.append(
            {
                "method": "generate_structured",
                "messages": messages,
                "schema": output_schema.__name__,
                "response": result,
            }
        )
        return result  # type: ignore[no-any-return]

    def as_runnable(self) -> Runnable[Any, Any]:
        return RunnableLambda(lambda x: self.generate(x))

    def reset_log(self) -> None:
        self.call_log.clear()

    @staticmethod
    def _default_for(annotation: Any) -> Any:
        """Return a sensible default for common Pydantic field types."""
        origin = getattr(annotation, "__origin__", None)
        if origin is list:
            return []
        if origin is dict:
            return {}
        if annotation is str:
            return ""
        if annotation is float:
            return 0.5
        if annotation is int:
            return 0
        return None
