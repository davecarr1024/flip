from flip.bytes import Byte
from flip.components.controller import Instruction, Step

s1 = Step.create(controls={"c1", "c2"})
s2 = Step.create(controls={"c2", "c3"})
i = Instruction.create(
    name="i",
    opcode=Byte(0),
    statuses={"s1": False, "s2": True},
    steps=[s1, s2],
)


def test_create() -> None:
    assert i.name == "i"
    assert i.opcode == Byte(0)
    assert i.statuses == {"s1": False, "s2": True}
    assert i.steps == (s1, s2)


def test_get_controls() -> None:
    assert i.controls == {"c1", "c2", "c3"}


def test_with_steps() -> None:
    s3 = Step.create(controls={"c3", "c4"})
    assert i.with_steps([s3]) == Instruction.create(
        name="i",
        opcode=Byte(0),
        statuses={"s1": False, "s2": True},
        steps=[s3],
    )


def test_with_header() -> None:
    s3 = Step.create(controls={"c3", "c4"})
    assert i.with_header([s3]) == Instruction.create(
        name="i",
        opcode=Byte(0),
        statuses={"s1": False, "s2": True},
        steps=[s3, s1, s2],
    )


def test_with_footer() -> None:
    s3 = Step.create(controls={"c3", "c4"})
    assert i.with_footer([s3]) == Instruction.create(
        name="i",
        opcode=Byte(0),
        statuses={"s1": False, "s2": True},
        steps=[s1, s2, s3],
    )
