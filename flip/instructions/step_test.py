from flip.instructions import Step


def test_create() -> None:
    s = Step.create({"a", "b"})
    assert set(s) == {"a", "b"}
    assert len(s) == 2


def test_create_empty() -> None:
    s = Step.create()
    assert set(s) == set()
    assert len(s) == 0


def test_ctor_empty() -> None:
    s = Step()
    assert set(s) == set()
    assert len(s) == 0


def test_with_control() -> None:
    assert set(Step().with_control("a")) == {"a"}


def test_with_controls() -> None:
    assert set(Step().with_controls({"a", "b"})) == {"a", "b"}
