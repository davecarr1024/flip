from flip.bytes import Byte
from flip.instructions import (
    AddressingMode,
    Instruction,
    InstructionImpl,
    InstructionMode,
    InstructionSet,
    Step,
)

i1 = Instruction.create(
    name="i1",
    modes={
        InstructionMode.create(
            mode=AddressingMode.IMMEDIATE,
            opcode=Byte(0x01),
            impls={
                InstructionImpl.create(
                    statuses={"a": True, "b": False},
                    steps=[Step.create({"c1", "c2"}), Step.create({"c2", "c3"})],
                ),
                InstructionImpl.create(
                    statuses={"c": False, "d": True},
                    steps=[Step.create({"c3", "c4"}), Step.create({"c4", "c5"})],
                ),
            },
        ),
        InstructionMode.create(
            mode=AddressingMode.ABSOLUTE,
            opcode=Byte(0x02),
            impls={
                InstructionImpl.create(
                    statuses={"e": True, "f": True},
                    steps=[Step.create({"c5", "c6"}), Step.create({"c6", "c7"})],
                ),
            },
        ),
    },
)
i2 = Instruction.create(
    name="i2",
    modes={
        InstructionMode.create(
            mode=AddressingMode.IMMEDIATE,
            opcode=Byte(0x03),
            impls={
                InstructionImpl.create(
                    statuses={"a": True, "b": False},
                    steps=[Step.create({"c1", "c2"}), Step.create({"c2", "c3"})],
                ),
            },
        ),
    },
)
i3 = Instruction.create(
    name="i3",
    modes={
        InstructionMode.create(
            mode=AddressingMode.IMMEDIATE,
            opcode=Byte(0x04),
            impls={
                InstructionImpl.create(
                    statuses={"a": True, "b": False},
                    steps=[Step.create({"c1", "c2"}), Step.create({"c2", "c3"})],
                ),
            },
        ),
    },
)
is_ = InstructionSet.create({i1, i2})


def test_create() -> None:
    assert set(is_) == {i1, i2}
    assert len(is_) == 2


def test_create_empty() -> None:
    assert set(InstructionSet.create()) == set()


def test_ctor_empty() -> None:
    assert set(InstructionSet()) == set()


def test_with_instructions() -> None:
    assert set(is_.with_instructions({i3})) == {i1, i2, i3}


def test_with_instruction() -> None:
    assert set(is_.with_instruction(i3)) == {i1, i2, i3}


def test_with_header() -> None:
    s1 = Step().with_control("ch1")
    s2 = Step().with_control("ch2")
    assert set(is_.with_header({s1, s2})) == {i.with_header({s1, s2}) for i in {i1, i2}}


def test_with_footer() -> None:
    s1 = Step().with_control("cf1")
    s2 = Step().with_control("cf2")
    assert set(is_.with_footer({s1, s2})) == {i.with_footer({s1, s2}) for i in {i1, i2}}


def test_controls() -> None:
    assert is_.controls == {"c1", "c2", "c3", "c4", "c5", "c6", "c7"}


def test_statuses() -> None:
    assert is_.statuses == {"a", "b", "c", "d", "e", "f"}
