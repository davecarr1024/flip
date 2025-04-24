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
            steps=[
                Step.create({"c1", "c2"}),
                Step.create({"c2", "c3"}),
            ],
        ),
        InstructionImpl.create(
            statuses={"c": False, "d": True},
            steps=[
                Step.create({"c3", "c4"}),
                Step.create({"c4", "c5"}),
                Step.create({"c3", "c4"}),
            ],
        ),
    },
)
im2 = InstructionMode.create(
    mode=AddressingMode.ABSOLUTE,
    opcode=Byte(0x02),
    impls={
        InstructionImpl.create(
            statuses={"e": True, "f": False},
            steps=[
                Step.create({"c5", "c6"}),
                Step.create({"c6", "c7"}),
            ],
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


def test_ctor_empty() -> None:
    assert set(Instruction(name="i")) == set()


def test_with_modes() -> None:
    assert set(i.with_modes({im3})) == {im1, im2, im3}


def test_with_mode() -> None:
    assert set(i.with_mode(im3)) == {im1, im2, im3}


def test_with_header() -> None:
    s1 = Step().with_control("ch1")
    s2 = Step().with_control("ch2")
    assert set(i.with_header({s1, s2})) == {
        im.with_header({s1, s2}) for im in {im1, im2}
    }


def test_with_footer() -> None:
    s1 = Step().with_control("cf1")
    s2 = Step().with_control("cf2")
    assert set(i.with_footer({s1, s2})) == {
        im.with_footer({s1, s2}) for im in {im1, im2}
    }


def test_create_simple() -> None:
    s1 = Step.create({"c1", "c2"})
    s2 = Step.create({"c2", "c3"})
    i = Instruction.create_simple(
        name="i",
        mode=AddressingMode.IMMEDIATE,
        opcode=Byte(0x01),
        steps=[s1, s2],
    )
    assert i.name == "i"
    assert len(i) == 1
    im = next(iter(i))
    assert im.mode == AddressingMode.IMMEDIATE
    assert im.opcode == Byte(0x01)
    assert len(im) == 1
    ii = next(iter(im))
    assert ii.statuses == {}
    assert list(ii) == [s1, s2]


def test_controls() -> None:
    assert i.controls == {"c1", "c2", "c3", "c4", "c5", "c6", "c7"}


def test_statuses() -> None:
    assert i.statuses == {"a", "b", "c", "d", "e", "f"}


def test_max_num_steps() -> None:
    assert i.max_num_steps == 3
