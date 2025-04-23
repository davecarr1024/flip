from flip.bytes import Byte, Word
from flip.components import Component, Rom


def test_ctor() -> None:
    p = Component(name="p")
    rom = Rom(
        name="r", parent=p, data={Word(0x0000): Byte(0x00), Word(0x0001): Byte(0x01)}
    )
    assert rom.name == "r"
    assert rom.parent is p
    assert p.children == {rom}
    assert rom.path == "r"
    assert rom[Word(0x0000)] == Byte(0x00)
    assert rom[Word(0x0001)] == Byte(0x01)
    assert len(rom) == 2
    assert dict(rom) == {Word(0x0000): Byte(0x00), Word(0x0001): Byte(0x01)}
    assert Word(0x0003) not in rom
