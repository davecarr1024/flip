import pytest

from flip.components import Bus, Register


def test_ctor() -> None:
    bus = Bus()
    reg = Register(name="reg", bus=bus)
    assert reg.bus is bus
    assert reg.value == 0
    assert not reg.write_enable
    assert not reg.read_enable
    assert reg.name == "reg"


def test_write() -> None:
    bus = Bus()
    reg = Register(name="reg", bus=bus, parent=bus)
    reg.write_enable = True
    reg.value = 1
    bus.tick_write()
    assert bus.value == 1
    assert bus.setter == "Bus.reg"


def test_write_conflict() -> None:
    bus = Bus()
    r1 = Register(name="r1", bus=bus, parent=bus)
    r2 = Register(name="r2", bus=bus, parent=bus)
    r1.write_enable = True
    r1.value = 1
    r2.write_enable = True
    r2.value = 2
    with pytest.raises(Bus.ConflictError):
        bus.tick()


def test_read() -> None:
    bus = Bus()
    reg = Register(name="reg", bus=bus, parent=bus)
    bus.set(1, "test")
    reg.read_enable = True
    bus.tick_read()
    assert reg.value == 1


def test_read_open_bus() -> None:
    bus = Bus()
    reg = Register(name="reg", bus=bus, parent=bus)
    reg.read_enable = True
    with pytest.raises(Register.ReadError):
        bus.tick()


def test_write_and_read() -> None:
    bus = Bus()
    r1 = Register(name="r1", bus=bus, parent=bus)
    r2 = Register(name="r2", bus=bus, parent=bus)
    r1.write_enable = True
    r1.value = 1
    r2.read_enable = True
    bus.tick()
    assert r2.value == 1
