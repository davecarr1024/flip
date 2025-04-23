import pytest

from flip.bytes import Byte, Word
from flip.components import Component, Ram


def test_ctor() -> None:
    p = Component(name="p")
    ram = Ram(
        name="r", parent=p, data={Word(0x0000): Byte(0x00), Word(0x0001): Byte(0x01)}
    )
    assert ram.name == "r"
    assert ram.parent is p
    assert p.children == {ram}
    assert ram.path == "r"
    assert ram[Word(0x0000)] == Byte(0x00)
    assert ram[Word(0x0001)] == Byte(0x01)
    assert len(ram) == 2
    assert dict(ram) == {Word(0x0000): Byte(0x00), Word(0x0001): Byte(0x01)}
    assert Word(0x0003) not in ram


def test_setitem() -> None:
    ram = Ram()
    assert Word(0x0000) not in ram
    ram[Word(0x0000)] = Byte(0x00)
    assert ram[Word(0x0000)] == Byte(0x00)


def test_delitem() -> None:
    ram = Ram(data={Word(0x0000): Byte(0x00)})
    assert ram[Word(0x0000)] == Byte(0x00)
    del ram[Word(0x0000)]
    assert Word(0x0000) not in ram


def test_delitem_notfound() -> None:
    ram = Ram()
    with pytest.raises(Ram.KeyError):
        del ram[Word(0x0000)]
