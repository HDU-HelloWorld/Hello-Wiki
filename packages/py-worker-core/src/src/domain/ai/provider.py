from abc import ABC, abstractmethod
from typing import Any, TypeVar

from langchain_core.runnables import Runnable
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProviderPort(ABC):
    """Domain-layer abstraction for LLM interactions.

    Application use cases depend only on this port — never on
    LangChain or any specific API implementation.
    """

    @abstractmethod
    async def generate(self, messages: list[dict[str, str]]) -> str: ...

    @abstractmethod
    async def generate_structured(
        self, messages: list[dict[str, str]], output_schema: type[T]
    ) -> T: ...

    @abstractmethod
    def as_runnable(self) -> Runnable[Any, Any]: ...
