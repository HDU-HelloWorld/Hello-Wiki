from dataclasses import dataclass


@dataclass
class TagRow:
    name: str
    label: str
    level: int
    is_leaf: bool


def serialize_tag_tree(tags: list[TagRow]) -> str:
    """Serialize a flat list of tag rows (ordered by ltree path) into
    an indented text tree for injection into the extraction prompt."""
    lines: list[str] = []
    for t in tags:
        indent = "  " * t.level
        if t.is_leaf:
            lines.append(f"{indent}{t.name} — {t.label}")
        else:
            lines.append(f"{indent}{t.name}")
    return "\n".join(lines)
