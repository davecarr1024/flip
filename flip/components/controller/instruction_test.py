from flip.bytes import Byte
from flip.components.controller import Instruction, Step


def test_create() -> None:
    s1 = Step.create(controls={"c1", "c2"})
    s2 = Step.create(controls={"c3", "c4"})
    i = Instruction.create(
        opcode=Byte(0),
        statuses={"s1": False, "s2": True},
        steps=[s1, s2],
    )
    assert i.opcode == Byte(0)
    assert i.statuses == {"s1": False, "s2": True}
    assert i.steps == (s1, s2)


def test_get_controls() -> None:
    assert Instruction.create(
        opcode=Byte(0),
        statuses={},
        steps=[
            Step(controls=frozenset({"c1", "c2"})),
            Step(controls=frozenset({"c2", "c3"})),
        ],
    ).controls == {"c1", "c2", "c3"}
