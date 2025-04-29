from flip.bytes import Byte
from flip.components.controller import StatusMapping
from flip.instructions import (
    AddressingMode,
    Instruction,
    InstructionImpl,
    InstructionMode,
    InstructionSet,
    Step,
)

sm = StatusMapping(
    instruction_set=InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.IMMEDIATE,
                        opcode=Byte(0),
                        impls={
                            InstructionImpl.create(
                                statuses={"s1": False, "s2": True},
                                steps=[
                                    Step.create(controls={"c1", "c2"}),
                                    Step.create(controls={"c2", "c3"}),
                                ],
                            ),
                            InstructionImpl.create(
                                statuses={"s2": True, "s3": False},
                                steps=[
                                    Step.create(controls={"c3", "c4"}),
                                    Step.create(controls={"c4", "c5"}),
                                ],
                            ),
                        },
                    )
                },
            ),
        }
    )
)


def test_status_mapping() -> None:
    assert sm == {"s1": 0, "s2": 1, "s3": 2}
    assert sm["s1"] == 0
    assert "s4" not in sm
    assert len(sm) == 3


def test_encode_address() -> None:
    assert sm.encode_address({"s1": True, "s2": True, "s3": False}) == 0b011


def test_encode_address_with_extra_statuses() -> None:
    assert sm.encode_address({"s1": True, "s2": True, "s3": False, "s4": True}) == 0b011


def test_decode_address() -> None:
    assert sm.decode_address(0b011) == {"s1": True, "s2": True, "s3": False}
