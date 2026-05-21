from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field

from src.application.init.commands import InitTagsCommand
from src.domain.ai.provider import LLMProviderPort


class LeafTag(BaseModel):
    name: str
    label: str
    description: str = ""


class Category(BaseModel):
    name: str
    label: str
    description: str = ""
    leaves: list[LeafTag] = Field(default_factory=list)


class TagTreeSchema(BaseModel):
    domain: str
    generated_at: str = ""
    categories: list[Category] = Field(default_factory=list)


class InitTagsUseCase:
    """Generate the initial domain tag hierarchy by calling the LLM with the
    tag-initialize skill's domain-specific prompt."""

    SKILLS_BASE = Path("apps/skills/tag-initialize/references")

    def __init__(self, provider: LLMProviderPort) -> None:
        self._provider = provider

    async def execute(self, command: InitTagsCommand) -> TagTreeSchema:
        index = self._load_index()
        ref = self._resolve_reference(index, command.domain)
        prompt = self._load_prompt(ref["prompt"])
        system_prompt = (
            prompt.replace("{domain}", command.domain)
            .replace("{description}", command.description)
            .replace("{language}", command.language)
            .replace("{existing_tags}", "[]")
        )
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": command.description},
        ]
        return await self._provider.generate_structured(messages, TagTreeSchema)

    def _load_index(self) -> dict[str, Any]:
        index_path = self.SKILLS_BASE / "index.yaml"
        with open(index_path, encoding="utf-8") as f:
            return yaml.safe_load(f)  # type: ignore[no-any-return]

    def _resolve_reference(self, index: dict[str, Any], domain: str) -> dict[str, Any]:
        for ref in index["references"]:
            if ref["id"] == domain:
                return ref  # type: ignore[no-any-return]
        fallback = next(r for r in index["references"] if r.get("default"))
        return fallback  # type: ignore[no-any-return]

    def _load_prompt(self, prompt_path: str) -> str:
        full_path = self.SKILLS_BASE / prompt_path
        with open(full_path, encoding="utf-8") as f:
            return f.read()
