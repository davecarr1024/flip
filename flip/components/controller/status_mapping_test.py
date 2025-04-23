from flip.bytes import Byte
from flip.components.controller import Instruction, InstructionSet, StatusMapping

sm = StatusMapping(
    InstructionSet.create(
        instructions={
            Instruction.create(
                name="i1",
                opcode=Byte(0),
                statuses={
                    "A": True,
                    "B": False,
                },
                steps=[],
            ),
            Instruction.create(
                name="i2",
                opcode=Byte(1),
                statuses={
                    "B": True,
                    "C": False,
                },
                steps=[],
            ),
        }
    )
)


def test_status_mapping() -> None:
    assert sm == {"A": 0, "B": 1, "C": 2}
    assert sm["A"] == 0
    assert "D" not in sm
    assert len(sm) == 3


def test_encode_address() -> None:
    assert sm.encode_address({"A": True, "B": True, "C": False}) == 0b011


def test_decode_address() -> None:
    assert sm.decode_address(0b011) == {"A": True, "B": True, "C": False}
