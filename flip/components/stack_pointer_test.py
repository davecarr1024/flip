from flip.bytes import Byte, Word
from flip.components import Bus, StackPointer


def test_ctor() -> None:
    sp = StackPointer(
        name="sp",
        bus=Bus(),
        high_value=Byte(0x01),
    )
    assert sp.value == Word(0x0100)


def test_idle() -> None:
    sp = StackPointer(
        name="sp",
        bus=Bus(),
        high_value=Byte(0x01),
    )
    sp.increment = False
    sp.decrement = False
    assert not sp.increment
    assert not sp.decrement
    assert sp.value == Word(0x0100)
    sp.tick()
    assert not sp.increment
    assert not sp.decrement
    assert sp.value == Word(0x0100)


def test_increment() -> None:
    sp = StackPointer(
        name="sp",
        bus=Bus(),
        high_value=Byte(0x01),
    )
    sp.increment = True
    sp.decrement = False
    assert sp.increment
    assert not sp.decrement
    assert sp.value == Word(0x0100)
    sp.tick()
    assert not sp.increment
    assert not sp.decrement
    assert sp.value == Word(0x0101)


def test_decrement() -> None:
    sp = StackPointer(
        name="sp",
        bus=Bus(),
        high_value=Byte(0x01),
    )
    sp.increment = False
    sp.decrement = True
    assert not sp.increment
    assert sp.decrement
    assert sp.value == Word(0x0100)
    sp.tick()
    assert not sp.increment
    assert not sp.decrement
    assert sp.value == Word(0x01FF)
