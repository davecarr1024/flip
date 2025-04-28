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
