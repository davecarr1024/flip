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


def test_lda_index_x() -> None:
    computer = (
        MinimalComputer.program_builder()
        .ldx(0x02)
        .lda_index_x("data")
        .hlt()
        .at(0x100)
        .label("data")
        .data(0x10, 0x20, 0x30)
        .run()
    )
    assert computer.a.value == Byte(0x30)


def test_lda_index_y() -> None:
    computer = (
        MinimalComputer.program_builder()
        .ldy(0x02)
        .lda_index_y("data")
        .hlt()
        .at(0x100)
        .label("data")
        .data(0x10, 0x20, 0x30)
        .run()
    )
    assert computer.a.value == Byte(0x30)


def test_sta_absolute() -> None:
    computer = (
        MinimalComputer.program_builder()
        .lda(0xAB)
        .sta("label")
        .hlt()
        .at(0xBEEF)
        .label("label")
        .data(Byte(0x00))
        .run()
    )
    assert computer.memory[Word(0xBEEF)] == Byte(0xAB)


def test_sta_zero_page() -> None:
    computer = (
        MinimalComputer.program_builder()
        .at(0xBEEF)
        .lda(0xAB)
        .sta_zero_page(0x12)
        .hlt()
        .load()
    )
    computer.program_counter.value = Word(0xBEEF)
    computer.tick_until_halt()
    assert computer.memory[Word(0x0012)] == Byte(0xAB)


def test_sta_index_x() -> None:
    computer = (
        MinimalComputer.program_builder()
        .ldx(0x02)
        .lda(0xAB)
        .sta_index_x("data")
        .hlt()
        .at(0x100)
        .label("data")
        .data(0x10, 0x20, 0x30)
        .run()
    )
    assert computer.memory[Word(0x102)] == Byte(0xAB)


def test_sta_index_y() -> None:
    computer = (
        MinimalComputer.program_builder()
        .ldy(0x02)
        .lda(0xAB)
        .sta_index_y("data")
        .hlt()
        .at(0x100)
        .label("data")
        .data(0x10, 0x20, 0x30)
        .run()
    )
    assert computer.memory[Word(0x102)] == Byte(0xAB)


def test_ldx_immediate() -> None:
    computer = MinimalComputer.program_builder().ldx(0x03).hlt().run()
    assert computer.x.value == Byte(0x03)


def test_ldx_absolute() -> None:
    computer = (
        MinimalComputer.program_builder()
        .ldx("label")
        .hlt()
        .label("label")
        .data(Byte(0xAB))
        .run()
    )
    assert computer.x.value == Byte(0xAB)


def test_ldx_zero_page() -> None:
    computer = (
        MinimalComputer.program_builder()
        .at(0x12)
        .data(0xAB)
        .at(0x100)
        .ldx_zero_page(0x12)
        .hlt()
        .load()
    )
    computer.program_counter.value = Word(0x100)
    computer.tick_until_halt()
    assert computer.x.value == Byte(0xAB)


def test_stx_absolute() -> None:
    computer = (
        MinimalComputer.program_builder()
        .ldx(0xAB)
        .stx("label")
        .hlt()
        .at(0xBEEF)
        .label("label")
        .data(Byte(0x00))
        .run()
    )
    assert computer.memory[Word(0xBEEF)] == Byte(0xAB)


def test_stx_zero_page() -> None:
    computer = (
        MinimalComputer.program_builder()
        .at(0xBEEF)
        .ldx(0xAB)
        .stx_zero_page(0x12)
        .hlt()
        .load()
    )
    computer.program_counter.value = Word(0xBEEF)
    computer.tick_until_halt()
    assert computer.memory[Word(0x0012)] == Byte(0xAB)


def test_ldy_immediate() -> None:
    computer = MinimalComputer.program_builder().ldy(0x03).hlt().run()
    assert computer.y.value == Byte(0x03)


def test_ldy_absolute() -> None:
    computer = (
        MinimalComputer.program_builder()
        .ldy("label")
        .hlt()
        .label("label")
        .data(Byte(0xAB))
        .run()
    )
    assert computer.y.value == Byte(0xAB)


def test_ldy_zero_page() -> None:
    computer = (
        MinimalComputer.program_builder()
        .at(0x12)
        .data(0xAB)
        .at(0x100)
        .ldy_zero_page(0x12)
        .hlt()
        .load()
    )
    computer.program_counter.value = Word(0x100)
    computer.tick_until_halt()
    assert computer.y.value == Byte(0xAB)


def test_sty_absolute() -> None:
    computer = (
        MinimalComputer.program_builder()
        .ldy(0xAB)
        .sty("label")
        .hlt()
        .at(0xBEEF)
        .label("label")
        .data(Byte(0x00))
        .run()
    )
    assert computer.memory[Word(0xBEEF)] == Byte(0xAB)


def test_sty_zero_page() -> None:
    computer = (
        MinimalComputer.program_builder()
        .at(0xBEEF)
        .ldy(0xAB)
        .sty_zero_page(0x12)
        .hlt()
        .load()
    )
    computer.program_counter.value = Word(0xBEEF)
    computer.tick_until_halt()
    assert computer.memory[Word(0x0012)] == Byte(0xAB)


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


def test_beq_absolute_no_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0
        .lda(0x00)
        # a += 1
        .adc(0x01)
        # if a == 0, jump to end
        # not expected to jump
        .beq("end")
        # a = 5
        .lda(0x05)
        # hlt
        .label("end")
        .hlt()
        .run()
    )
    # assert that we did not jump
    assert computer.a.value == Byte(0x05)


def test_beq_absolute_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0
        .lda(0x00)
        # a += 0
        .adc(0x00)
        # if a == 0, jump to end
        # expected to jump
        .beq("end")
        # a = 5
        .lda(0x05)
        # hlt
        .label("end")
        .hlt()
        .run()
    )
    # assert that we did jump
    assert computer.a.value == Byte(0x00)


def test_bmi_absolute_no_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0
        .lda(0x00)
        # a += 1
        .adc(0x01)
        # if a < 0, jump to end
        # not expected to jump
        .bmi("end")
        # a = 5
        .lda(0x05)
        # hlt
        .label("end")
        .hlt()
        .run()
    )
    # assert that we did not jump
    assert computer.a.value == Byte(0x05)


def test_bmi_absolute_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0
        .lda(0x00)
        # a -= 1
        .adc(0xFF)
        # if a < 0, jump to end
        # expected to jump
        .bmi("end")
        # a = 5
        .lda(0x05)
        # hlt
        .label("end")
        .hlt()
        .run()
    )
    # assert that we did jump
    assert computer.a.value == Byte(0xFF)


def test_bcs_absolute_no_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0
        .lda(0x00)
        # a += 1
        .adc(0x01)
        # if carry, jump to end
        # not expected to jump
        .bcs("end")
        # a = 5
        .lda(0x05)
        # hlt
        .label("end")
        .hlt()
        .run()
    )
    # assert that we did not jump
    assert computer.a.value == Byte(0x05)


def test_bcs_absolute_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0
        .lda(0xFF)
        # a += 1
        .adc(0x01)
        # if carry, jump to end
        # expected to jump
        .bcs("end")
        # a = 5
        .lda(0x05)
        # hlt
        .label("end")
        .hlt()
        .run()
    )
    # assert that we did jump
    assert computer.a.value == Byte(0x00)


def test_bvs_absolute_no_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0
        .lda(0x00)
        # a += 1
        .adc(0x01)
        # if overflow, jump to end
        # not expected to jump
        .bvs("end")
        # a = 5
        .lda(0x05)
        # hlt
        .label("end")
        .hlt()
        .run()
    )
    # assert that we did not jump
    assert computer.a.value == Byte(0x05)


def test_bvs_absolute_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0x7F
        .lda(0x7F)
        # a += 1
        .adc(0x01)
        # if overflow, jump to end
        # expected to jump
        .bvs("end")
        # a = 5
        .lda(0x05)
        # hlt
        .label("end")
        .hlt()
        .run()
    )
    # assert that we did jump
    assert computer.a.value == Byte(0x80)


def test_bne_absolute_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        .lda(0x00)
        .adc(0x01)  # a = 1 → zero flag not set
        .bne("end")  # should jump
        .lda(0x05)
        .label("end")
        .hlt()
        .run()
    )
    assert computer.a.value == Byte(0x01)


def test_bne_absolute_no_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        .lda(0x00)
        .adc(0x00)  # a = 0 → zero flag set
        .bne("end")  # should not jump
        .lda(0x05)
        .label("end")
        .hlt()
        .run()
    )
    assert computer.a.value == Byte(0x05)


def test_bpl_absolute_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        .lda(0x00)
        .adc(0x01)  # a = 1 → negative flag not set
        .bpl("end")  # should jump
        .lda(0x05)
        .label("end")
        .hlt()
        .run()
    )
    assert computer.a.value == Byte(0x01)


def test_bpl_absolute_no_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        .lda(0x00)
        .adc(0xFF)  # a = -1 → negative flag set
        .bpl("end")  # should not jump
        .lda(0x05)
        .label("end")
        .hlt()
        .run()
    )
    assert computer.a.value == Byte(0x05)


def test_bcc_absolute_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        .lda(0x00)
        .adc(0x01)  # no carry
        .bcc("end")  # should jump
        .lda(0x05)
        .label("end")
        .hlt()
        .run()
    )
    assert computer.a.value == Byte(0x01)


def test_bcc_absolute_no_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        .lda(0xFF)
        .adc(0x01)  # causes carry
        .bcc("end")  # should not jump
        .lda(0x05)
        .label("end")
        .hlt()
        .run()
    )
    assert computer.a.value == Byte(0x05)


def test_bvc_absolute_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        .lda(0x00)
        .adc(0x01)  # no overflow
        .bvc("end")  # should jump
        .lda(0x05)
        .label("end")
        .hlt()
        .run()
    )
    assert computer.a.value == Byte(0x01)


def test_bvc_absolute_no_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        .lda(0x7F)
        .adc(0x01)  # overflow
        .bvc("end")  # should not jump
        .lda(0x05)
        .label("end")
        .hlt()
        .run()
    )
    assert computer.a.value == Byte(0x05)


def test_sbc_immediate() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 5
        .lda(0x05)
        # set carry (no borrow)
        .sec()
        # a -= 2
        .sbc(0x02)
        # hlt
        .hlt().run()
    )
    # check result
    assert computer.a.value == Byte(0x03)


def test_sbc_absolute() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 5
        .lda(0x05)
        # set carry (no borrow)
        .sec()
        # a -= 2
        .sbc("label")
        # hlt
        .hlt()
        # label
        .label("label")
        .data(Byte(0x02))
        .run()
    )
    # check result
    assert computer.a.value == Byte(0x03)


def test_and_immediate() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0b0011
        .lda(0b0011)
        # a &= 0b0101
        .and_(0b0101)
        # hlt
        .hlt().run()
    )
    # check result
    assert computer.a.value == Byte(0x01)


def test_and_absolute() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0b0011
        .lda(0b0011)
        # a &= 0b0101
        .and_("label")
        # hlt
        .hlt()
        # label
        .label("label")
        .data(Byte(0b0101))
        .run()
    )
    # check result
    assert computer.a.value == Byte(0x01)


def test_ora_immediate() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0b0011
        .lda(0b0011)
        # a |= 0b0101
        .ora(0b0101)
        # hlt
        .hlt().run()
    )
    # check result
    assert computer.a.value == Byte(0b0111)


def test_ora_absolute() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0b0011
        .lda(0b0011)
        # a |= 0b0101
        .ora("label")
        # hlt
        .hlt()
        # label
        .label("label")
        .data(Byte(0b0101))
        .run()
    )
    # check result
    assert computer.a.value == Byte(0b0111)


def test_eor_immediate() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0b0011
        .lda(0b0011)
        # a ^= 0b0101
        .eor(0b0101)
        # hlt
        .hlt().run()
    )
    # check result
    assert computer.a.value == Byte(0b0110)


def test_eor_absolute() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0b0011
        .lda(0b0011)
        # a ^= 0b0101
        .eor("label")
        # hlt
        .hlt()
        # label
        .label("label")
        .data(Byte(0b0101))
        .run()
    )
    # check result
    assert computer.a.value == Byte(0b0110)


def test_asl() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0b0011
        .lda(0b0011)
        # a <<= 1
        .asl()
        # hlt
        .hlt().run()
    )
    # check result
    assert computer.a.value == Byte(0b0110)


def test_lsr() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0b0011
        .lda(0b0011)
        # a >>= 1
        .lsr()
        # hlt
        .hlt().run()
    )
    # check result
    assert computer.a.value == Byte(0b0001)


def test_rol() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0b0011
        .lda(0b0011)
        # set carry - this will be shifted in
        .sec()
        # a <<= 1
        .rol()
        # hlt
        .hlt().run()
    )
    # check result
    assert computer.a.value == Byte(0b0111)


def test_ror() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0b0011
        .lda(0b0011)
        # set carry - this will be shifted in
        .sec()
        # a >>= 1
        .ror()
        # hlt
        .hlt().run()
    )
    # check result
    assert computer.a.value == Byte(0b1000_0001)


def test_cmp_immediate_no_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 1
        .lda(0x01)
        # compare a with 2
        .cmp(0x02)
        # branch if equal - not expected to jump
        .beq("end")
        # a = 5
        .lda(0x05)
        # end
        .label("end")
        .hlt()
        .run()
    )
    assert computer.a.value == Byte(0x05)


def test_cmp_immediate_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 1
        .lda(0x01)
        # compare a with 1
        .cmp(0x01)
        # branch if equal - expected to jump
        .beq("end")
        # a = 5
        # not expected to run
        .lda(0x05)
        # end
        .label("end")
        .hlt()
        .run()
    )
    assert computer.a.value == Byte(0x01)


def test_cmp_absolute_no_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 1
        .lda(0x01)
        # compare a with 2
        .cmp("label")
        # branch if equal - not expected to jump
        .beq("end")
        # a = 5
        .lda(0x05)
        # end
        .label("end")
        .hlt()
        .label("label")
        .data(Byte(0x02))
        .run()
    )
    assert computer.a.value == Byte(0x05)


def test_cmp_absolute_jump() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 1
        .lda(0x01)
        # compare a with 1
        .cmp("label")
        # branch if equal - expected to jump
        .beq("end")
        # a = 5
        # not expected to run
        .lda(0x05)
        # end
        .label("end")
        .hlt()
        .label("label")
        .data(Byte(0x01))
        .run()
    )
    assert computer.a.value == Byte(0x01)
