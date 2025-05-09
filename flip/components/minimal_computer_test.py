from pytest_subtests import SubTests

from flip.bytes import Byte, Word
from flip.components import MinimalComputer
from flip.programs import Program


def test_statuses() -> None:
    assert set(MinimalComputer().statuses_by_path.keys()) == {
        "alu.carry_out",
        "alu.half_carry",
        "alu.negative",
        "alu.overflow",
        "alu.zero",
        "result_analyzer.negative",
        "result_analyzer.zero",
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


def test_load_instructions_set_status(subtests: SubTests) -> None:
    for instruction in list[str](["lda", "ldx", "ldy"]):
        for arg, zero, negative in list[tuple[Program.Instruction.Arg, bool, bool]](
            [
                (
                    Program.Instruction.Immediate(Byte(0x00)),
                    True,
                    False,
                ),
                (
                    Program.Instruction.Immediate(Byte(0x01)),
                    False,
                    False,
                ),
                (
                    Program.Instruction.Immediate(Byte(0x80)),
                    False,
                    True,
                ),
                (
                    Program.Instruction.Absolute("zero_data"),
                    True,
                    False,
                ),
                (
                    Program.Instruction.Absolute("one_data"),
                    False,
                    False,
                ),
                (
                    Program.Instruction.Absolute("negative_data"),
                    False,
                    True,
                ),
                (
                    Program.Instruction.ZeroPage(Byte(0x03)),
                    True,
                    False,
                ),
                (
                    Program.Instruction.ZeroPage(Byte(0x04)),
                    False,
                    False,
                ),
                (
                    Program.Instruction.ZeroPage(Byte(0x05)),
                    False,
                    True,
                ),
            ]
        ):
            with subtests.test(
                instruction=instruction,
                arg=arg,
                zero=zero,
                negative=negative,
            ):
                computer = (
                    MinimalComputer.program_builder()
                    .instruction(instruction, arg)
                    .hlt()
                    .label("zero_data")
                    .data(0x00)
                    .label("one_data")
                    .data(0x01)
                    .label("negative_data")
                    .data(0x80)
                    .run()
                )
                status_values = computer.controller.status.status_values
                assert status_values["result_analyzer.zero"] == zero
                assert status_values["result_analyzer.negative"] == negative


def test_lda_index_sets_status(subtests: SubTests) -> None:
    for index_instruction, index_arg, arg, zero, negative in list[
        tuple[
            str,
            Program.Instruction.Immediate,
            Program.Instruction.IndexX | Program.Instruction.IndexY,
            bool,
            bool,
        ]
    ](
        [
            (
                "ldx",
                Program.Instruction.Immediate(Byte(0x00)),
                Program.Instruction.IndexX("data"),
                True,
                False,
            ),
            (
                "ldx",
                Program.Instruction.Immediate(Byte(0x01)),
                Program.Instruction.IndexX("data"),
                False,
                False,
            ),
            (
                "ldx",
                Program.Instruction.Immediate(Byte(0x02)),
                Program.Instruction.IndexX("data"),
                False,
                True,
            ),
            (
                "ldy",
                Program.Instruction.Immediate(Byte(0x00)),
                Program.Instruction.IndexY("data"),
                True,
                False,
            ),
            (
                "ldy",
                Program.Instruction.Immediate(Byte(0x01)),
                Program.Instruction.IndexY("data"),
                False,
                False,
            ),
            (
                "ldy",
                Program.Instruction.Immediate(Byte(0x02)),
                Program.Instruction.IndexY("data"),
                False,
                True,
            ),
        ]
    ):
        with subtests.test(
            index_instruction=index_instruction,
            index_arg=index_arg,
            arg=arg,
            zero=zero,
            negative=negative,
        ):
            computer = (
                MinimalComputer.program_builder()
                .instruction(index_instruction, index_arg)
                .instruction("lda", arg)
                .hlt()
                .label("data")
                .data(0x00)
                .data(0x01)
                .data(0x80)
                .run()
            )
            status_values = computer.controller.status.status_values
            assert status_values["result_analyzer.zero"] == zero
            assert status_values["result_analyzer.negative"] == negative


def test_increment(subtests: SubTests) -> None:
    for instruction, register in list[
        tuple[
            MinimalComputer.ProgramBuilder.Statement,
            str,
        ]
    ](
        [
            (lambda b: b.inc(), "a"),
            (lambda b: b.inx(), "x"),
            (lambda b: b.iny(), "y"),
        ]
    ):
        for value, expected, zero, negative in list[tuple[Byte, Byte, bool, bool]](
            [
                (
                    Byte(0xFF),
                    Byte(0x00),
                    True,
                    False,
                ),
                (
                    Byte(0x00),
                    Byte(0x01),
                    False,
                    False,
                ),
                (
                    Byte(0x7F),
                    Byte(0x80),
                    False,
                    True,
                ),
            ]
        ):
            with subtests.test(
                instruction=instruction,
                register=register,
                value=value,
                expected=expected,
                zero=zero,
                negative=negative,
            ):
                computer = (
                    MinimalComputer.program_builder()
                    .instruction(f"ld{register}", value)
                    .apply(instruction)
                    .hlt()
                    .run()
                )
                assert computer.registers_by_name[register].value == expected
                status_values = computer.controller.status.status_values
                assert status_values["result_analyzer.zero"] == zero
                assert status_values["result_analyzer.negative"] == negative


def test_decrement(subtests: SubTests) -> None:
    for instruction, register in list[
        tuple[
            MinimalComputer.ProgramBuilder.Statement,
            str,
        ]
    ](
        [
            (lambda b: b.dec(), "a"),
            (lambda b: b.dex(), "x"),
            (lambda b: b.dey(), "y"),
        ]
    ):
        for value, expected, zero, negative in list[tuple[Byte, Byte, bool, bool]](
            [
                (
                    Byte(0x00),
                    Byte(0xFF),
                    False,
                    True,
                ),
                (
                    Byte(0x01),
                    Byte(0x00),
                    True,
                    False,
                ),
                (
                    Byte(0x80),
                    Byte(0x7F),
                    False,
                    False,
                ),
            ]
        ):
            with subtests.test(
                instruction=instruction,
                register=register,
                value=value,
                expected=expected,
                zero=zero,
                negative=negative,
            ):
                computer = (
                    MinimalComputer.program_builder()
                    .instruction(f"ld{register}", value)
                    .apply(instruction)
                    .hlt()
                    .run()
                )
                assert computer.registers_by_name[register].value == expected
                status_values = computer.controller.status.status_values
                assert status_values["result_analyzer.zero"] == zero
                assert status_values["result_analyzer.negative"] == negative


def test_pha() -> None:
    computer = MinimalComputer.program_builder().lda(0x01).pha().hlt().run()
    assert computer.memory[Word(0x01FF)] == Byte(0x01)
    assert computer.stack_pointer.value == Word(0x01FE)


def test_pla() -> None:
    computer = (
        MinimalComputer.program_builder().lda(0x01).pha().lda(0x02).pla().hlt().run()
    )
    assert computer.a.value == Byte(0x01)


def test_php() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0: P = Z
        .lda(0x00)
        # push P = Z
        .php()
        # a = FF: P = N
        .lda(0xFF)
        .hlt()
        .run()
    )
    # expect P = Z is on the stack
    assert computer.memory[Word(0x01FF)] == computer.controller.status.format.encode(
        {"result_analyzer.zero": True}
    )
    assert computer.stack_pointer.value == Word(0x01FE)
    # expect current P = N
    assert (
        computer.controller.status.format.encode({"result_analyzer.negative": True})
        == computer.controller.status.value
    )


def test_plp() -> None:
    computer = (
        MinimalComputer.program_builder()
        # a = 0: P = Z
        .lda(0x00)
        # push P = Z
        .php()
        # a = FF: P = N
        .lda(0xFF)
        # pull P = Z
        .plp()
        .hlt()
        .run()
    )
    # expect P = Z
    assert (
        computer.controller.status.format.encode({"result_analyzer.zero": True})
        == computer.controller.status.value
    ), str(computer.controller.status.status_values)
    # expect A = FF - N
    assert computer.a.value == Byte(0xFF)


def test_jsr() -> None:
    computer = (
        MinimalComputer.program_builder()
        .lda(0x01)
        .jsr("subroutine")
        .jsr("subroutine")
        .hlt()
        .label("subroutine")
        .inc()
        .rts()
        .run()
    )
    assert computer.a.value == Byte(0x03)


def test_nested_jsr() -> None:
    computer = (
        MinimalComputer.program_builder()
        .lda(0x01)
        .ldx(0x01)
        .jsr("inc_x_once_and_a_twice")
        .hlt()
        .label("inc_x_once_and_a_twice")
        .jsr("inc_x")
        .jsr("inc_a")
        .jsr("inc_a")
        .rts()
        .label("inc_x")
        .inx()
        .rts()
        .label("inc_a")
        .inc()
        .rts()
        .run()
    )
    assert computer.a.value == Byte(0x03)
    assert computer.x.value == Byte(0x02)
