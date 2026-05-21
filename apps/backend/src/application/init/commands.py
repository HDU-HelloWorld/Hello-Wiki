from dataclasses import dataclass


@dataclass(frozen=True)
class InitTagsCommand:
    domain: str
    description: str
    language: str = "zh"
