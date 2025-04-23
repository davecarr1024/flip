import pytest

from flip.bytes import Byte, Word
from flip.components import Bus, Component, Memory, Register


def test_ctor() -> None:
    bus = Bus(name="bus")
    memory = Memory(name="memory", bus=bus, parent=bus)
    assert memory.address == Word(0)
    assert memory.value == Byte(0)
    assert not memory.read
    assert not memory.write
    assert len(memory) == 0
    assert dict(memory) == {}


def test_ctor_data() -> None:
    bus = Bus(name="bus")
    memory = Memory(name="memory", bus=bus, parent=bus, data={Word(0): Byte(1)})
    assert len(memory) == 1
    assert dict(memory) == {Word(0): Byte(1)}
    assert memory[Word(0)] == Byte(1)
    assert Word(1) not in memory


def test_address() -> None:
    bus = Bus(name="bus")
    memory = Memory(name="memory", bus=bus, parent=bus)
    memory.address = Word(0x1234)
    assert memory.address == Word(0x1234)


def test_value() -> None:
    bus = Bus(name="bus")
    memory = Memory(name="memory", bus=bus, parent=bus)
    memory.address = Word(0x1234)
    memory.value = Byte(0x56)
    assert memory.value == Byte(0x56)
    assert memory[Word(0x1234)] == Byte(0x56)
    memory.address = Word(0x1235)
    assert memory.value == Byte(0x00)


def test_delitem() -> None:
    bus = Bus(name="bus")
    memory = Memory(name="memory", bus=bus, parent=bus)
    memory[Word(0x1234)] = Byte(0x56)
    assert memory[Word(0x1234)] == Byte(0x56)
    del memory[Word(0x1234)]
    assert Word(0x1234) not in memory


def test_delitem_notfound() -> None:
    bus = Bus(name="bus")
    memory = Memory(name="memory", bus=bus, parent=bus)
    with pytest.raises(Memory.KeyError):
        del memory[Word(0x1234)]


def test_read() -> None:
    root = Component()
    bus = Bus(name="bus", parent=root)
    memory = Memory(name="memory", bus=bus, parent=root)
    memory.address = Word(0x1234)
    memory.read = True
    a = Register(name="a", bus=bus, parent=root)
    a.value = Byte(0x56)
    a.write = True
    root.tick()
    assert memory[Word(0x1234)] == Byte(0x56)


def test_read_open_bus() -> None:
    root = Component()
    bus = Bus(name="bus", parent=root)
    memory = Memory(name="memory", bus=bus, parent=root)
    memory.address = Word(0x1234)
    memory.read = True
    with pytest.raises(Memory.ReadError):
        root.tick()


def test_write() -> None:
    root = Component()
    bus = Bus(name="bus", parent=root)
    memory = Memory(name="memory", bus=bus, parent=root)
    memory.address = Word(0x1234)
    memory[Word(0x1234)] = Byte(0x56)
    memory.write = True
    a = Register(name="a", bus=bus, parent=root)
    a.read = True
    root.tick()
    assert a.value == Byte(0x56)
