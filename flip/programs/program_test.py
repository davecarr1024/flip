import pytest

from flip.bytes import Byte, Word
from flip.instructions import InstructionSet
from flip.programs import Program

instruction_set = (
    InstructionSet.builder()
    .instruction("nop", 0x00)
    .step()
    .instruction("lda")
    .mode("immediate", 0x01)
    .step()
    .mode("absolute", 0x02)
    .step()
    .mode("zero_page", 0x03)
    .step()
    .instruction("only_supports_immediate")
    .mode("immediate", 0x03)
    .step()
    .build()
)
program = Program(instruction_set=instruction_set)


def test_empty() -> None:
    assert program.statements == []
    assert program.assemble().memory == {}


def test_with_value_byte() -> None:
    assert program.with_value(Byte(0x01)).assemble().memory == {
        Word(0x0000): Byte(0x01)
    }


def test_with_value_word() -> None:
    assert program.with_value(Word(0xBEEF)).assemble().memory == {
        Word(0x0000): Byte(0xEF),
        Word(0x0001): Byte(0xBE),
    }


def test_with_values() -> None:
    assert program.with_values([Byte(0x01), Byte(0x02)]).assemble().memory == {
        Word(0x0000): Byte(0x01),
        Word(0x0001): Byte(0x02),
    }


def test_label() -> None:
    assert program.with_ref("label").at_position(Word(0xBEEF)).with_label(
        "label"
    ).assemble().memory == {Word(0x0000): Byte(0xEF), Word(0x0001): Byte(0xBE)}


def test_instruction_no_arg() -> None:
    assert program.with_statement(Program.Instruction("nop")).assemble().memory == {
        Word(0x0000): Byte(0x00)
    }


def test_instruction_immediate() -> None:
    assert (
        program.with_statement(
            Program.Instruction("lda", Program.Instruction.Immediate(Byte(0x10)))
        )
    ).assemble().memory == {Word(0x0000): Byte(0x01), Word(0x0001): Byte(0x10)}


def test_instruction_absolute_value() -> None:
    assert program.with_statement(
        Program.Instruction("lda", Program.Instruction.Absolute(Word(0xBEEF)))
    ).assemble().memory == {
        Word(0x0000): Byte(0x02),
        Word(0x0001): Byte(0xEF),
        Word(0x0002): Byte(0xBE),
    }


def test_instruction_absolute_ref() -> None:
    assert program.with_statement(
        Program.Instruction("lda", Program.Instruction.Absolute("label"))
    ).at_position(Word(0xBEEF)).with_label("label").assemble().memory == {
        Word(0x0000): Byte(0x02),
        Word(0x0001): Byte(0xEF),
        Word(0x0002): Byte(0xBE),
    }


def test_instruction_zero_page() -> None:
    assert program.with_statement(
        Program.Instruction("lda", Program.Instruction.ZeroPage(Byte(0x10)))
    ).assemble().memory == {
        Word(0x0000): Byte(0x03),
        Word(0x0001): Byte(0x10),
    }


def test_instruction_not_found() -> None:
    with pytest.raises(Program.Instruction.InstructionNotFound):
        program.with_statement(Program.Instruction("not_found")).assemble()


def test_instruction_mode_not_found() -> None:
    with pytest.raises(Program.Instruction.InstructionModeNotFound):
        program.with_statement(
            Program.Instruction(
                "only_supports_immediate", Program.Instruction.Absolute(Word(0xBEEF))
            )
        ).assemble()
