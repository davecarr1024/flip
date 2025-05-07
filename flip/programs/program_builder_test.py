import pytest

from flip.bytes import Byte, Word
from flip.programs import Program, ProgramBuilder

from .program_test import instruction_set, program

program_builder = ProgramBuilder.for_instruction_set(instruction_set)


def test_empty() -> None:
    assert program_builder.build() == program


def test_instruction_none() -> None:
    assert program_builder.instruction("nop").build() == program.with_statement(
        Program.Instruction("nop")
    )


def test_instruction_immediate_int() -> None:
    assert program_builder.instruction("lda", 0x10).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.Immediate(Byte(0x10)))
    )


def test_instruction_immediate_byte() -> None:
    assert program_builder.instruction(
        "lda", Byte(0x10)
    ).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.Immediate(Byte(0x10)))
    )


def test_instruction_absolute_str() -> None:
    assert program_builder.instruction(
        "lda", "label"
    ).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.Absolute("label"))
    )


def test_immediate_int() -> None:
    assert program_builder.instruction("lda").immediate(
        0x10
    ).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.Immediate(Byte(0x10)))
    )


def test_immediate_byte() -> None:
    assert program_builder.instruction("lda").immediate(
        Byte(0x10)
    ).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.Immediate(Byte(0x10)))
    )


def test_absolute_int() -> None:
    assert program_builder.instruction("lda").absolute(
        0xBEEF
    ).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.Absolute(Word(0xBEEF)))
    )


def test_absolute_word() -> None:
    assert program_builder.instruction("lda").absolute(
        Word(0xBEEF)
    ).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.Absolute(Word(0xBEEF)))
    )


def test_absolute_str() -> None:
    assert program_builder.instruction("lda").absolute(
        "label"
    ).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.Absolute("label"))
    )


def test_zero_page_int() -> None:
    assert program_builder.instruction("lda").zero_page(
        0x10
    ).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.ZeroPage(Byte(0x10)))
    )


def test_zero_page_byte() -> None:
    assert program_builder.instruction("lda").zero_page(
        Byte(0x10)
    ).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.ZeroPage(Byte(0x10)))
    )


def test_index_x_int() -> None:
    assert program_builder.instruction("lda").index_x(
        0xBEEF
    ).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.IndexX(Word(0xBEEF)))
    )


def test_index_x_word() -> None:
    assert program_builder.instruction("lda").index_x(
        Word(0xBEEF)
    ).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.IndexX(Word(0xBEEF)))
    )


def test_index_x_str() -> None:
    assert program_builder.instruction("lda").index_x(
        "label"
    ).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.IndexX("label"))
    )


def test_index_y_int() -> None:
    assert program_builder.instruction("lda").index_y(
        0xBEEF
    ).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.IndexY(Word(0xBEEF)))
    )


def test_index_y_word() -> None:
    assert program_builder.instruction("lda").index_y(
        Word(0xBEEF)
    ).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.IndexY(Word(0xBEEF)))
    )


def test_index_y_str() -> None:
    assert program_builder.instruction("lda").index_y(
        "label"
    ).build() == program.with_statement(
        Program.Instruction("lda", Program.Instruction.IndexY("label"))
    )


def test_label() -> None:
    assert program_builder.label("label").build() == program.with_label("label")


def test_at_int() -> None:
    assert program_builder.at(0xBEEF).build() == program.at_position(Word(0xBEEF))


def test_at_word() -> None:
    assert program_builder.at(Word(0xBEEF)).build() == program.at_position(Word(0xBEEF))


def test_no_instruction() -> None:
    with pytest.raises(ProgramBuilder.NoInstruction):
        program_builder.immediate(0x10).build()


def test_duplicate_arg() -> None:
    with pytest.raises(ProgramBuilder.DuplicateArg):
        program_builder.instruction("lda", 0x10).immediate(0x10).build()


def test_data() -> None:
    assert program_builder.data(Byte(0x01), Byte(0x02)).build() == program.with_values(
        [Byte(0x01), Byte(0x02)]
    )


def test_pending_instruction_then_label() -> None:
    assert (
        program_builder.instruction("lda", "label").label("label").data(0xAB).build()
    ) == (
        program.with_statement(
            Program.Instruction("lda", Program.Instruction.Absolute("label"))
        )
        .with_label("label")
        .with_value(Byte(0xAB))
    )


def test_pending_instruction_then_at() -> None:
    assert (
        program_builder.instruction("lda", "label").at(0xBEEF).data(0xAB).build()
    ) == (
        program.with_statement(
            Program.Instruction("lda", Program.Instruction.Absolute("label"))
        )
        .at_position(Word(0xBEEF))
        .with_value(Byte(0xAB))
    )


def test_pending_instruction_then_data() -> None:
    assert (program_builder.instruction("lda", "label").data(0xAB).build()) == (
        program.with_statement(
            Program.Instruction("lda", Program.Instruction.Absolute("label"))
        ).with_value(Byte(0xAB))
    )
