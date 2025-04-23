from flip.bytes import Byte
from flip.instructions import (
    AddressingMode,
    Instruction,
    InstructionImpl,
    InstructionMode,
    Step,
)

im1 = InstructionMode.create(
    mode=AddressingMode.IMMEDIATE,
    opcode=Byte(0x01),
    impls={
        InstructionImpl.create(
            statuses={"a": True, "b": False},
            steps={Step.create({"c1", "c2"}), Step.create({"c2", "c3"})},
        ),
        InstructionImpl.create(
            statuses={"a": False, "b": True},
            steps={Step.create({"c3", "c4"}), Step.create({"c4", "c5"})},
        ),
    },
)
im2 = InstructionMode.create(
    mode=AddressingMode.ABSOLUTE,
    opcode=Byte(0x02),
    impls={
        InstructionImpl.create(
            steps={Step.create({"c5", "c6"}), Step.create({"c6", "c7"})},
        ),
    },
)
im3 = InstructionMode.create(
    mode=AddressingMode.RELATIVE,
    opcode=Byte(0x03),
    impls={
        InstructionImpl.create(
            steps={Step.create({"c7", "c8"}), Step.create({"c8", "c9"})},
        ),
    },
)
i = Instruction.create(name="i", modes={im1, im2})


def test_create() -> None:
    assert i.name == "i"
    assert set(i) == {im1, im2}
    assert len(i) == 2


def test_create_empty() -> None:
    assert set(Instruction.create(name="i")) == set()


def test_with_modes() -> None:
    assert set(i.with_modes({im3})) == {im1, im2, im3}


def test_with_mode() -> None:
    assert set(i.with_mode(im3)) == {im1, im2, im3}
