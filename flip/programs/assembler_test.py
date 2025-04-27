import pytest

from flip.bytes import Byte, Word
from flip.instructions import InstructionSet
from flip.programs import Assembler

assembler = Assembler(instruction_set=InstructionSet())


def test_duplicate_position() -> None:
    with pytest.raises(Assembler.Output.DuplicatePosition):
        assembler.with_value(Byte(0x01)).with_next_position(Word(0x0000)).with_value(
            Byte(0x02)
        ).assemble()


def test_unknown_label() -> None:
    with pytest.raises(Assembler.Ref.LabelNotFound):
        assembler.with_ref("unknown").assemble()


def test_duplicate_label() -> None:
    with pytest.raises(Assembler.DuplicateLabel):
        assembler.with_label("duplicate").with_next_position(Word(0x0001)).with_label(
            "duplicate"
        ).assemble()
