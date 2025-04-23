from flip.instructions import InstructionImpl, Step

s1 = Step.create({"c1", "c2"})
s2 = Step.create({"c2", "c3"})
s3 = Step.create({"c3", "c4"})
ii = InstructionImpl.create(
    statuses={"a": True, "b": False},
    steps=[s1, s2],
)


def test_create() -> None:
    assert ii.statuses == {"a": True, "b": False}
    assert list(ii) == [s1, s2]
    assert len(ii) == 2


def test_create_empty() -> None:
    ii = InstructionImpl.create()
    assert ii.statuses == {}
    assert list(ii) == []
    assert len(ii) == 0


def test_ctor_empty() -> None:
    ii = InstructionImpl()
    assert ii.statuses == {}
    assert list(ii) == []
    assert len(ii) == 0


def test_with_steps() -> None:
    assert list(ii.with_steps([s3])) == [s1, s2, s3]


def test_with_header() -> None:
    assert list(ii.with_header([s3])) == [s3, s1, s2]


def test_with_footer() -> None:
    assert list(ii.with_footer([s3])) == [s1, s2, s3]


def test_with_step() -> None:
    assert list(ii.with_step(s3)) == [s1, s2, s3]


def test_controls() -> None:
    assert ii.controls == {"c1", "c2", "c3"}
