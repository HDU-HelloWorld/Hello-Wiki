from pathlib import Path

from pydantic import BaseModel, Field

from src.domain.ai.provider import LLMProviderPort


class SuggestedTag(BaseModel):
    name: str
    label: str
    description: str = ""
    parent_hint: str = ""


class EffectiveRange(BaseModel):
    start: str | None = None
    end: str | None = None
    description: str = ""
    stale_risk: str = "unknown"


class ExtractedKnowledge(BaseModel):
    """5-field REQUIRED extraction template."""

    chunk_summary: str = Field(min_length=1)
    page_title: str = Field(min_length=1)
    compiled_truth: str = Field(min_length=1)
    suggested_tags: list[SuggestedTag] = Field(min_length=2, max_length=6)
    effective_range: EffectiveRange


SKILLS_BASE = Path(__file__).resolve().parents[4] / "skills" / "knowledge-extraction" / "references"


class SkillPromptLoader:
    """Loads domain-specific prompt from the knowledge-extraction skill."""

    @staticmethod
    def load(domain: str) -> str:
        index_path = SKILLS_BASE / "index.yaml"
        import yaml

        with open(index_path, encoding="utf-8") as f:
            index = yaml.safe_load(f)
        ref = next((r for r in index["references"] if r["id"] == domain), None)
        if ref is None:
            ref = next(r for r in index["references"] if r.get("default"))
        prompt_path = SKILLS_BASE / ref["prompt"]
        with open(prompt_path, encoding="utf-8") as f:
            return f.read()


class StructuredExtractionAdapter:
    """Two-message LLM extraction: system prompt (rules) + user prompt (tag tree + chunk text)."""

    def __init__(self, provider: LLMProviderPort) -> None:
        self._provider = provider

    async def extract(
        self,
        domain: str,
        chunk_text: str,
        tag_tree: str,
        source_document: str = "",
        source_page: str = "",
        chunk_index: int = 0,
        total_chunks: int = 1,
    ) -> ExtractedKnowledge:
        system_prompt = SkillPromptLoader.load(domain)
        system_prompt = (
            system_prompt.replace("{source_document}", source_document)
            .replace("{source_page}", source_page)
            .replace("{chunk_index}", str(chunk_index))
            .replace("{total_chunks}", str(total_chunks))
        )
        user_prompt = f"AVAILABLE TAGS\n{tag_tree}\n\nTEXT TO ANALYZE\n{chunk_text}"
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        return await self._provider.generate_structured(messages, ExtractedKnowledge)
