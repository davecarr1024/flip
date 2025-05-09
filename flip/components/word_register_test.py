from flip.bytes import Byte, Word
from flip.components import Bus, Component, WordRegister


def test_value() -> None:
    root = Component()
    bus = Bus(name="bus", parent=root)
    reg = WordRegister(name="reg", bus=bus, parent=root)
    reg.value = Word(0x1234)
    assert reg.value == Word(0x1234)


def test_low() -> None:
    root = Component()
    bus = Bus(name="bus", parent=root)
    reg = WordRegister(name="reg", bus=bus, parent=root)
    reg.low = Byte(0x34)
    assert reg.low == Byte(0x34)
    assert reg.value == Word(0x0034)


def test_high() -> None:
    root = Component()
    bus = Bus(name="bus", parent=root)
    reg = WordRegister(name="reg", bus=bus, parent=root)
    reg.high = Byte(0x12)
    assert reg.high == Byte(0x12)
    assert reg.value == Word(0x1200)


def test_ctor_value() -> None:
    assert WordRegister(
        name="reg",
        bus=Bus(),
        low_value=Byte(0x34),
        high_value=Byte(0x12),
    ).value == Word(0x1234)
