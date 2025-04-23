from flip.bytes import Byte
from flip.instructions import AddressingMode, InstructionImpl, InstructionMode, Step

ii1 = InstructionImpl.create(
    statuses={"a": True, "b": False},
    steps=[Step.create({"c1", "c2"}), Step.create({"c2", "c3"})],
)
ii2 = InstructionImpl.create(
    statuses={"b": False, "c": True},
    steps=[Step.create({"c3", "c4"}), Step.create({"c4", "c5"})],
)
ii3 = InstructionImpl.create(
    statuses={"c": True, "d": True},
    steps=[Step.create({"c5", "c6"}), Step.create({"c6", "c7"})],
)
im = InstructionMode.create(
    mode=AddressingMode.IMMEDIATE,
    opcode=Byte(0x01),
    impls={ii1, ii2},
)


def test_create() -> None:
    assert im.mode == AddressingMode.IMMEDIATE
    assert im.opcode == Byte(0x01)
    assert set(im) == {ii1, ii2}
    assert len(im) == 2


def test_create_empty() -> None:
    assert (
        set(InstructionMode.create(mode=AddressingMode.IMMEDIATE, opcode=Byte(0x01)))
        == set()
    )


def test_with_impls() -> None:
    assert set(im.with_impls({ii3})) == {ii1, ii2, ii3}


def test_with_impl() -> None:
    assert set(im.with_impl(ii3)) == {ii1, ii2, ii3}


def test_with_header() -> None:
    s1 = Step().with_control("ch1")
    s2 = Step().with_control("ch2")
    assert set(im.with_header({s1, s2})) == {
        ii.with_header({s1, s2}) for ii in {ii1, ii2}
    }


def test_with_footer() -> None:
    s1 = Step().with_control("cf1")
    s2 = Step().with_control("cf2")
    assert set(im.with_footer({s1, s2})) == {
        ii.with_footer({s1, s2}) for ii in {ii1, ii2}
    }


def test_controls() -> None:
    assert im.controls == {"c1", "c2", "c3", "c4", "c5"}


def test_statuses() -> None:
    assert im.statuses == {"a", "b", "c"}
