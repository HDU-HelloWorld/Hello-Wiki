from typing import Any, TypeVar

from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, SecretStr

from src.core.config import settings
from src.domain.ai.provider import LLMProviderPort

T = TypeVar("T", bound=BaseModel)


class OpenAICompatibleProvider(LLMProviderPort):
    """Production LLM provider wrapping LangChain's ChatOpenAI.

    Compatible with any OpenAI-format API: DeepSeek, OpenAI, vLLM, etc.
    """

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        temperature: float | None = None,
    ) -> None:
        resolved_api_key = api_key or settings.LLM_API_KEY or None
        self._model = ChatOpenAI(
            model=model or settings.LLM_MODEL_NAME,
            api_key=SecretStr(resolved_api_key) if resolved_api_key else None,
            base_url=base_url or settings.LLM_BASE_URL,
            temperature=temperature or settings.LLM_TEMPERATURE,
            model_kwargs={"extra_body": {"thinking": {"type": "disabled"}}},
        )

    async def generate(self, messages: list[dict[str, str]]) -> str:
        result = await self._model.ainvoke(messages)
        return str(result.content)

    async def generate_structured(
        self, messages: list[dict[str, str]], output_schema: type[T]
    ) -> T:
        structured_model = self._model.with_structured_output(output_schema, method="json_mode")
        return await structured_model.ainvoke(messages)  # type: ignore[return-value]

    def as_runnable(self) -> Runnable[Any, Any]:
        return self._model
