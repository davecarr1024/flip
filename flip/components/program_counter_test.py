from flip.bytes import Byte, Word
from flip.components import Bus, ProgramCounter


def test_ctor() -> None:
    bus = Bus(name="bus")
    pc = ProgramCounter(name="pc", bus=bus, parent=bus)
    assert pc.low == Byte(0)
    assert pc.high == Byte(0)
    assert pc.value == Word(0)
    assert not pc.increment
    assert not pc.reset


def test_low() -> None:
    bus = Bus(name="bus")
    pc = ProgramCounter(name="pc", bus=bus, parent=bus)
    pc.low = Byte(1)
    assert pc.low == Byte(1)
    assert pc.high == Byte(0)
    assert pc.value == Word(1)


def test_high() -> None:
    bus = Bus(name="bus")
    pc = ProgramCounter(name="pc", bus=bus, parent=bus)
    pc.high = Byte(1)
    assert pc.low == Byte(0)
    assert pc.high == Byte(1)
    assert pc.value == Word(0x100)


def test_value() -> None:
    bus = Bus(name="bus")
    pc = ProgramCounter(name="pc", bus=bus, parent=bus)
    pc.value = Word(0x1234)
    assert pc.low == Byte(0x34)
    assert pc.high == Byte(0x12)
    assert pc.value == Word(0x1234)


def test_increment() -> None:
    bus = Bus(name="bus")
    pc = ProgramCounter(name="pc", bus=bus, parent=bus)
    pc.increment = True
    assert pc.value == Word(0)
    bus.tick()
    assert pc.value == Word(1)


def test_reset() -> None:
    bus = Bus(name="bus")
    pc = ProgramCounter(name="pc", bus=bus, parent=bus)
    pc.reset = True
    pc.value = Word(1)
    assert pc.value == Word(1)
    bus.tick()
    assert pc.value == Word(0)
