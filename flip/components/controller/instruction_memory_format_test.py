from flip.bytes import Byte
from flip.components.controller import (
    Instruction,
    InstructionMemoryFormat,
    InstructionSet,
    Step,
)

imf = InstructionMemoryFormat(
    instruction_set=InstructionSet.create(
        instructions={
            Instruction.create(
                opcode=Byte(0),
                statuses={"s1": False, "s2": True},
                steps=[
                    Step.create(controls={"c1", "c2"}),
                    Step.create(controls={"c2", "c3"}),
                ],
            ),
            Instruction.create(
                opcode=Byte(1),
                statuses={"s2": True, "s3": False},
                steps=[
                    Step.create(controls={"c3", "c4"}),
                    Step.create(controls={"c4", "c5"}),
                ],
            ),
        }
    )
)


def test_encode_address() -> None:
    assert (
        imf.encode_address(
            opcode=Byte(0x03),
            statuses={"s1": True, "s2": True, "s3": False},
            step_index=Byte(0x01),
        )
        == 0b11_011_1
    )


def test_decode_address() -> None:
    assert imf.decode_address(0b11_011_1) == (
        Byte(3),
        {"s1": True, "s2": True, "s3": False},
        Byte(1),
    )


def test_encode_controls() -> None:
    assert imf.encode_controls({"c1", "c2", "c4"}) == 0b01011


def test_decode_controls() -> None:
    assert imf.decode_controls(0b01011) == {"c1", "c2", "c4"}


def test_address_size() -> None:
    assert imf.address_size == 12


def test_control_size() -> None:
    assert imf.control_size == 5


def test_statuses() -> None:
    assert imf.statuses == {"s1": 0, "s2": 1, "s3": 2}


def test_controls() -> None:
    assert imf.controls == {"c1": 0, "c2": 1, "c3": 2, "c4": 3, "c5": 4}
