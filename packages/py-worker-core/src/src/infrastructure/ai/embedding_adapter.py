import httpx

from src.core.config import settings
from src.domain.ai.embedding_port import EmbeddingPort


class OpenAICompatibleEmbeddingAdapter(EmbeddingPort):
    """OpenAI-compatible embedding API (DeepSeek, OpenAI, vLLM, etc.)."""

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self._model = model or settings.EMBEDDING_MODEL
        self._api_key = api_key or settings.LLM_API_KEY
        self._base_url = (base_url or settings.LLM_BASE_URL).rstrip("/")

    async def embed(self, text: str) -> list[float]:
        if not self._api_key:
            raise RuntimeError("LLM_API_KEY is required for embedding generation")

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self._base_url}/embeddings",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
                json={"model": self._model, "input": text},
            )
            response.raise_for_status()
            payload = response.json()

        data = payload.get("data")
        if not isinstance(data, list) or not data:
            raise RuntimeError("Embedding API returned empty data")

        embedding = data[0].get("embedding") if isinstance(data[0], dict) else None
        if not isinstance(embedding, list):
            raise RuntimeError("Embedding API returned invalid embedding vector")

        return [float(value) for value in embedding]
