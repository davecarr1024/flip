from flip.bytes import Byte
from flip.components.controller import ControlMapping, Instruction, InstructionSet, Step


def test_mapping() -> None:
    cm = ControlMapping(
        InstructionSet.create(
            instructions={
                Instruction.create(
                    name="i1",
                    opcode=Byte(0),
                    statuses={},
                    steps=[Step.create(controls={"A", "B"})],
                ),
                Instruction.create(
                    name="i2",
                    opcode=Byte(1),
                    statuses={},
                    steps=[Step.create(controls={"B", "C"})],
                ),
            }
        )
    )
    assert cm == {"A": 0, "B": 1, "C": 2}
    assert len(cm) == 3
    assert cm["A"] == 0
    assert cm["B"] == 1
    assert cm["C"] == 2
    assert "D" not in cm


def test_encode_value() -> None:
    cm = ControlMapping(
        InstructionSet.create(
            instructions={
                Instruction.create(
                    name="i1",
                    opcode=Byte(0),
                    statuses={},
                    steps=[Step.create(controls={"A", "B"})],
                ),
                Instruction.create(
                    name="i2",
                    opcode=Byte(1),
                    statuses={},
                    steps=[Step.create(controls={"B", "C"})],
                ),
            }
        )
    )
    assert cm.encode_value({"A", "B"}) == 0b011


def test_decode_value() -> None:
    cm = ControlMapping(
        InstructionSet.create(
            instructions={
                Instruction.create(
                    name="i1",
                    opcode=Byte(0),
                    statuses={},
                    steps=[Step.create(controls={"A", "B"})],
                ),
                Instruction.create(
                    name="i2",
                    opcode=Byte(1),
                    statuses={},
                    steps=[Step.create(controls={"B", "C"})],
                ),
            }
        )
    )
    assert cm.decode_value(0b011) == {"A", "B"}
