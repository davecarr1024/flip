from flip.bytes import Byte, Word
from flip.components import MinimalComputer


def test_halt() -> None:
    computer = MinimalComputer()
    computer.memory[Word(0)] = Byte(0x01)
    assert not computer.halt
    computer.tick_until_halt()
    assert computer.halt
    assert computer.program_counter.value == Word(1)


def test_set_halt() -> None:
    computer = MinimalComputer()
    computer.halt = True
    assert computer.halt
    computer.tick_until_halt()
    assert computer.halt
    assert computer.program_counter.value == Word(0)


def test_nop_and_halt() -> None:
    computer = MinimalComputer()
    computer.memory[Word(0)] = Byte(0x00)
    computer.memory[Word(1)] = Byte(0x01)
    computer.tick_until_halt()
    assert computer.program_counter.value == Word(2)


def test_tax() -> None:
    computer = MinimalComputer()
    computer.memory[Word(0)] = Byte(0x02)
    computer.memory[Word(1)] = Byte(0x01)
    computer.a.value = Byte(0x03)
    computer.tick_until_halt()
    assert computer.program_counter.value == Word(2)
    assert computer.x.value == Byte(0x03)


def test_txa() -> None:
    computer = MinimalComputer()
    computer.memory[Word(0)] = Byte(0x03)
    computer.memory[Word(1)] = Byte(0x01)
    computer.x.value = Byte(0x03)
    computer.tick_until_halt()
    assert computer.program_counter.value == Word(2)
    assert computer.a.value == Byte(0x03)


def test_tay() -> None:
    computer = MinimalComputer()
    computer.memory[Word(0)] = Byte(0x04)
    computer.memory[Word(1)] = Byte(0x01)
    computer.a.value = Byte(0x03)
    computer.tick_until_halt()
    assert computer.program_counter.value == Word(2)
    assert computer.y.value == Byte(0x03)


def test_tya() -> None:
    computer = MinimalComputer()
    computer.memory[Word(0)] = Byte(0x05)
    computer.memory[Word(1)] = Byte(0x01)
    computer.y.value = Byte(0x03)
    computer.tick_until_halt()
    assert computer.program_counter.value == Word(2)
    assert computer.a.value == Byte(0x03)


def test_lda_immediate() -> None:
    computer = MinimalComputer()
    computer.memory[Word(0)] = Byte(0x06)
    computer.memory[Word(1)] = Byte(0x03)
    computer.memory[Word(2)] = Byte(0x01)
    computer.tick_until_halt()
    assert computer.program_counter.value == Word(3)
    assert computer.a.value == Byte(0x03)


def test_lda_absolute() -> None:
    computer = MinimalComputer()
    computer.memory[Word(0)] = Byte(0x07)
    computer.memory[Word(1)] = Byte(0xEF)
    computer.memory[Word(2)] = Byte(0xBE)
    computer.memory[Word(3)] = Byte(0x01)
    computer.memory[Word(0xBEEF)] = Byte(0xAB)
    computer.tick_until_halt()
    assert computer.program_counter.value == Word(4)
    assert computer.a.value == Byte(0xAB)


def test_lda_zero_page() -> None:
    computer = MinimalComputer()
    computer.memory[Word(0x0100)] = Byte(0x08)
    computer.memory[Word(0x0101)] = Byte(0x12)
    computer.memory[Word(0x0102)] = Byte(0x01)
    computer.memory[Word(0x0012)] = Byte(0xCD)
    computer.program_counter.value = Word(0x0100)
    computer.tick_until_halt()
    assert computer.program_counter.value == Word(0x0103)
    assert computer.a.value == Byte(0xCD)


def test_jmp_absolute() -> None:
    computer = MinimalComputer()
    computer.memory[Word(0)] = Byte(0x20)
    computer.memory[Word(1)] = Byte(0xEF)
    computer.memory[Word(2)] = Byte(0xBE)
    computer.memory[Word(3)] = Byte(0x01)
    computer.memory[Word(0xBEEF)] = Byte(0x01)
    computer.tick_until_halt()
    assert computer.program_counter.value == Word(0xBEF0)
