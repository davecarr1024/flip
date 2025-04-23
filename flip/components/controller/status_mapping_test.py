from flip.bytes import Byte
from flip.components.controller import Instruction, InstructionSet, StatusMapping


def test_status_mapping() -> None:
    sm = StatusMapping(
        InstructionSet.create(
            instructions={
                Instruction.create(
                    opcode=Byte(0),
                    statuses={
                        "A": True,
                        "B": False,
                    },
                    steps=[],
                ),
                Instruction.create(
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
    assert sm == {"A": 0, "B": 1, "C": 2}
    assert sm["A"] == 0
    assert "D" not in sm
    assert len(sm) == 3


def test_encode_address() -> None:
    sm = StatusMapping(
        InstructionSet.create(
            instructions={
                Instruction.create(
                    opcode=Byte(0),
                    statuses={
                        "A": True,
                        "B": False,
                    },
                    steps=[],
                ),
                Instruction.create(
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
    assert sm.encode_address({"A": True, "B": True, "C": False}) == 0b011


def test_decode_address() -> None:
    sm = StatusMapping(
        InstructionSet.create(
            instructions={
                Instruction.create(
                    opcode=Byte(0),
                    statuses={
                        "A": True,
                        "B": False,
                    },
                    steps=[],
                ),
                Instruction.create(
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
    assert sm.decode_address(0b011) == {"A": True, "B": True, "C": False}
