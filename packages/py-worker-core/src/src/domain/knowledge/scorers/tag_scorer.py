def tag_score(query_tags: list[str], page_tags: list[str]) -> float:
    """Half-life decay: exact match 1.0, child 0.5, parent 0.25; capped at 3.0."""
    if not query_tags or not page_tags:
        return 0.0

    score = 0.0
    for qt in query_tags:
        for pt in page_tags:
            if qt == pt:
                score += 1.0
            elif pt.startswith(f"{qt}.") or (pt.startswith(qt) and len(pt) > len(qt)):
                score += 0.5
            else:
                parent = pt.rsplit(".", 1)[0] if "." in pt else pt
                if qt.startswith(parent) and qt != pt:
                    score += 0.25
    return min(score, 3.0)
