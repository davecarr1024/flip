from flip.bytes import Byte, Word
from flip.components import MinimalComputer


def test_statuses() -> None:
    assert set(MinimalComputer().statuses_by_path.keys()) == {
        "alu.carry_out",
        "alu.half_carry",
        "alu.negative",
        "alu.overflow",
        "alu.zero",
    }


def test_load_data() -> None:
    assert dict(MinimalComputer(data={Word(0x0000): Byte(0x01)}).memory) == {
        Word(0x0000): Byte(0x01)
    }


def test_halt() -> None:
    computer = MinimalComputer.program_builder().hlt().run()
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
    computer = MinimalComputer.program_builder().nop().hlt().run()
    assert computer.program_counter.value == Word(2)


def test_tax() -> None:
    computer = MinimalComputer()
    computer.a.value = Byte(0x03)
    computer.run(MinimalComputer.program_builder().tax().hlt())
    assert computer.program_counter.value == Word(2)
    assert computer.x.value == Byte(0x03)


def test_txa() -> None:
    computer = MinimalComputer()
    computer.x.value = Byte(0x03)
    computer.run(MinimalComputer.program_builder().txa().hlt())
    assert computer.program_counter.value == Word(2)
    assert computer.a.value == Byte(0x03)


def test_tay() -> None:
    computer = MinimalComputer()
    computer.a.value = Byte(0x03)
    computer.run(MinimalComputer.program_builder().tay().hlt())
    assert computer.program_counter.value == Word(2)
    assert computer.y.value == Byte(0x03)


def test_tya() -> None:
    computer = MinimalComputer()
    computer.y.value = Byte(0x03)
    computer.run(MinimalComputer.program_builder().tya().hlt())
    assert computer.program_counter.value == Word(2)
    assert computer.a.value == Byte(0x03)


def test_lda_immediate() -> None:
    computer = MinimalComputer.program_builder().lda(0x03).hlt().run()
    assert computer.program_counter.value == Word(3)
    assert computer.a.value == Byte(0x03)


def test_lda_absolute() -> None:
    computer = (
        MinimalComputer.program_builder()
        .lda("label")
        .hlt()
        .label("label")
        .data(Byte(0xAB))
        .run()
    )
    assert computer.program_counter.value == Word(4)
    assert computer.a.value == Byte(0xAB)


def test_lda_zero_page() -> None:
    computer = MinimalComputer()
    computer.program_counter.value = Word(0x0100)
    computer.run(
        MinimalComputer.program_builder()
        .at(0x0012)
        .data(0xAB)
        .at(0x0100)
        .label("label")
        .lda_zero_page(0x12)
        .hlt()
    )
    assert computer.program_counter.value == Word(0x0103)
    assert computer.a.value == Byte(0xAB)


def test_jmp_absolute() -> None:
    computer = MinimalComputer.program_builder().jmp(0xBEEF).at(0xBEEF).hlt().run()
    assert computer.program_counter.value == Word(0xBEF0)


def test_adc_immediate() -> None:
    computer = MinimalComputer.program_builder().lda(0x01).adc(0x02).hlt().run()
    assert computer.a.value == Byte(0x03)


def test_adc_absolute() -> None:
    computer = (
        MinimalComputer.program_builder()
        .lda(0x01)
        .adc("label")
        .hlt()
        .label("label")
        .data(Byte(0x02))
        .run()
    )
    assert computer.a.value == Byte(0x03)


def test_sec() -> None:
    computer = MinimalComputer()
    computer.alu.carry_in = False
    assert not computer.alu.carry_in
    computer.run(MinimalComputer.program_builder().sec().hlt())
    assert computer.alu.carry_in


def test_clc() -> None:
    computer = MinimalComputer()
    computer.alu.carry_in = True
    assert computer.alu.carry_in
    computer.run(MinimalComputer.program_builder().clc().hlt())
    assert not computer.alu.carry_in
