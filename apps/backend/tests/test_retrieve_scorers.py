from src.domain.knowledge.scorers.tag_scorer import tag_score


def test_tag_score_exact_match() -> None:
    assert tag_score(["functional_area.registration"], ["functional_area.registration"]) == 1.0


def test_tag_score_child_match() -> None:
    score = tag_score(
        ["functional_area"],
        ["functional_area.registration_course"],
    )
    assert score == 0.5


def test_tag_score_caps_at_three() -> None:
    score = tag_score(
        ["a", "b", "c", "d"],
        ["a", "b", "c", "d"],
    )
    assert score == 3.0
