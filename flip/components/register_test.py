import pytest

from flip.bytes import Byte
from flip.components import Bus, Register


def test_ctor() -> None:
    bus = Bus()
    reg = Register(name="reg", bus=bus)
    assert reg.bus is bus
    assert reg.value == Byte(0)
    assert not reg.write
    assert not reg.read
    assert reg.name == "reg"


def test_write() -> None:
    bus = Bus()
    reg = Register(name="reg", bus=bus, parent=bus)
    reg.write = True
    reg.value = Byte(1)
    bus.tick_write()
    assert bus.value == Byte(1)
    assert bus.setter == "reg"


def test_write_conflict() -> None:
    bus = Bus()
    r1 = Register(name="r1", bus=bus, parent=bus)
    r2 = Register(name="r2", bus=bus, parent=bus)
    r1.write = True
    r1.value = Byte(1)
    r2.write = True
    r2.value = Byte(2)
    with pytest.raises(Bus.ConflictError):
        bus.tick()


def test_read() -> None:
    bus = Bus()
    reg = Register(name="reg", bus=bus, parent=bus)
    bus.set(Byte(1), "test")
    reg.read = True
    bus.tick_read()
    assert reg.value == Byte(1)


def test_read_open_bus() -> None:
    bus = Bus()
    reg = Register(name="reg", bus=bus, parent=bus)
    reg.read = True
    with pytest.raises(Register.ReadError):
        bus.tick()


def test_write_and_read() -> None:
    bus = Bus()
    r1 = Register(name="r1", bus=bus, parent=bus)
    r2 = Register(name="r2", bus=bus, parent=bus)
    r1.write = True
    r1.value = Byte(1)
    r2.read = True
    bus.tick()
    assert r2.value == Byte(1)


def test_reset() -> None:
    bus = Bus()
    reg = Register(name="reg", bus=bus, parent=bus)
    reg.value = Byte(1)
    assert reg.value == Byte(1)
    reg.reset = True
    reg.tick()
    assert reg.value == Byte(0)
