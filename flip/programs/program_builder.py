from dataclasses import dataclass, replace
from typing import Optional, Self

from flip.bytes import Byte, Word
from flip.core import Error, Errorable
from flip.instructions import InstructionSet
from flip.programs.program import Program


@dataclass(frozen=True)
class ProgramBuilder(Errorable):
    class Error(Error): ...

    class NoInstruction(Error): ...

    class DuplicateArg(Error): ...

    program: Program
    _pending_instruction: Optional[Program.Instruction] = None

    @classmethod
    def for_instruction_set(cls, instruction_set: InstructionSet) -> Self:
        return cls(program=Program(instruction_set=instruction_set))

    def _with_program(self, program: Program) -> Self:
        return replace(self, program=program)

    def _with_pending_instruction(
        self, instruction: Optional[Program.Instruction]
    ) -> Self:
        return replace(self, _pending_instruction=instruction)

    def _with_arg(self, arg: Program.Instruction.Arg) -> Self:
        if self._pending_instruction is None:
            raise self._error("No instruction to add arg to.", self.NoInstruction)
        if self._pending_instruction.arg is not None:
            raise self._error("Instruction already has an arg.", self.DuplicateArg)
        return self._with_pending_instruction(self._pending_instruction.with_arg(arg))

    def _collapse_pending_instruction(self) -> Self:
        if self._pending_instruction is not None:
            self = self._with_program(
                self.program.with_statement(self._pending_instruction)
            )._with_pending_instruction(None)
        return self

    def instruction(self, name: str, arg: int | Byte | str | None = None) -> Self:
        self = self._collapse_pending_instruction()
        match arg:
            case int():
                return self._with_pending_instruction(
                    Program.Instruction(name, Program.Instruction.Immediate(Byte(arg)))
                )
            case Byte():
                return self._with_pending_instruction(
                    Program.Instruction(name, Program.Instruction.Immediate(arg))
                )
            case str():
                return self._with_pending_instruction(
                    Program.Instruction(name, Program.Instruction.Absolute(arg))
                )
            case None:
                return self._with_pending_instruction(Program.Instruction(name))

    def immediate(self, arg: int | Byte) -> Self:
        match arg:
            case int():
                return self._with_arg(Program.Instruction.Immediate(Byte(arg)))
            case Byte():
                return self._with_arg(Program.Instruction.Immediate(arg))

    def absolute(self, arg: int | Word | str) -> Self:
        match arg:
            case int():
                return self._with_arg(Program.Instruction.Absolute(Word(arg)))
            case Word() | str():
                return self._with_arg(Program.Instruction.Absolute(arg))

    def zero_page(self, arg: int | Byte) -> Self:
        match arg:
            case int():
                return self._with_arg(Program.Instruction.ZeroPage(Byte(arg)))
            case Byte():
                return self._with_arg(Program.Instruction.ZeroPage(arg))

    def label(self, name: str) -> Self:
        self = self._collapse_pending_instruction()
        return self._with_program(self.program.with_label(name))

    def at(self, position: int | Word) -> Self:
        self = self._collapse_pending_instruction()
        match position:
            case int():
                return self._with_program(self.program.at_position(Word(position)))
            case Word():
                return self._with_program(self.program.at_position(position))

    def data(self, *values: Byte | int) -> Self:
        self = self._collapse_pending_instruction()
        byte_values = list[Byte]()
        for value in values:
            match value:
                case int():
                    byte_values.append(Byte(value))
                case Byte():
                    byte_values.append(value)
        return self._with_program(self.program.with_values(byte_values))

    def build(self) -> Program:
        self = self._collapse_pending_instruction()
        return self.program
