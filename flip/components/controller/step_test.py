from flip.components.controller import Step


def test_create() -> None:
    assert Step.create(controls={"A", "B"}) == Step(controls=frozenset({"A", "B"}))
