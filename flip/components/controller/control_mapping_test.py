from flip.bytes import Byte
from flip.components.controller import ControlMapping
from flip.instructions import AddressingMode, Instruction, InstructionSet, Step

cm = ControlMapping(
    InstructionSet.create(
        instructions={
            Instruction.create_simple(
                name="i1",
                mode=AddressingMode.NONE,
                opcode=Byte(0),
                steps=[Step.create(controls={"A", "B"})],
            ),
            Instruction.create_simple(
                name="i2",
                mode=AddressingMode.NONE,
                opcode=Byte(1),
                steps=[Step.create(controls={"B", "C"})],
            ),
        }
    )
)


def test_mapping() -> None:
    assert cm == {"A": 0, "B": 1, "C": 2}
    assert len(cm) == 3
    assert cm["A"] == 0
    assert cm["B"] == 1
    assert cm["C"] == 2
    assert "D" not in cm


def test_encode_value() -> None:
    assert cm.encode_value({"A", "B"}) == 0b011


def test_decode_value() -> None:
    assert cm.decode_value(0b011) == {"A", "B"}
