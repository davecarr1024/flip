from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from typing import Iterable, Optional, override

from flip.bytes import Byte, Word
from flip.core import Error, Errorable
from flip.instructions import AddressingMode, InstructionSet


@dataclass(frozen=True)
class Program(Errorable):
    class Error(Error): ...

    @dataclass(frozen=True)
    class Statement(Errorable, ABC):
        @abstractmethod
        def bind(
            self, assembler: "assembler_lib.Assembler"
        ) -> "assembler_lib.Assembler":
            """Bind this statement to the given assembler."""

    @dataclass(frozen=True)
    class Literal(Statement):
        values: list[Byte]

        @override
        def bind(
            self, assembler: "assembler_lib.Assembler"
        ) -> "assembler_lib.Assembler":
            return assembler.with_values(self.values)

    @dataclass(frozen=True)
    class Label(Statement):
        name: str

        @override
        def bind(
            self, assembler: "assembler_lib.Assembler"
        ) -> "assembler_lib.Assembler":
            return assembler.with_label(self.name)

    @dataclass(frozen=True)
    class Ref(Statement):
        name: str

        @override
        def bind(
            self, assembler: "assembler_lib.Assembler"
        ) -> "assembler_lib.Assembler":
            return assembler.with_ref(self.name)

    @dataclass(frozen=True)
    class Instruction(Statement):
        class Error(Error): ...

        class InstructionNotFound(Error): ...

        class InstructionModeNotFound(Error): ...

        @dataclass(frozen=True)
        class Arg(ABC):
            @abstractmethod
            def bind(
                self, assembler: "assembler_lib.Assembler"
            ) -> "assembler_lib.Assembler":
                """Bind this argument to the given assembler."""

            @abstractmethod
            def addressing_mode(self) -> AddressingMode:
                """Return the addressing mode for this argument."""

        @dataclass(frozen=True)
        class Absolute(Arg):
            value: str | Word

            @override
            def bind(
                self, assembler: "assembler_lib.Assembler"
            ) -> "assembler_lib.Assembler":
                match self.value:
                    case str():
                        return assembler.with_ref(self.value)
                    case Word():
                        return assembler.with_value(self.value)

            @override
            def addressing_mode(self) -> AddressingMode:
                return AddressingMode.ABSOLUTE

        @dataclass(frozen=True)
        class Immediate(Arg):
            value: Byte

            @override
            def bind(
                self, assembler: "assembler_lib.Assembler"
            ) -> "assembler_lib.Assembler":
                return assembler.with_value(self.value)

            @override
            def addressing_mode(self) -> AddressingMode:
                return AddressingMode.IMMEDIATE

        @dataclass(frozen=True)
        class ZeroPage(Arg):
            value: Byte

            @override
            def bind(
                self, assembler: "assembler_lib.Assembler"
            ) -> "assembler_lib.Assembler":
                return assembler.with_value(self.value)

            @override
            def addressing_mode(self) -> AddressingMode:
                return AddressingMode.ZERO_PAGE

        @dataclass(frozen=True)
        class IndexX(Arg):
            value: str | Word

            @override
            def bind(
                self,
                assembler: "assembler_lib.Assembler",
            ) -> "assembler_lib.Assembler":
                match self.value:
                    case str():
                        return assembler.with_ref(self.value)
                    case Word():
                        return assembler.with_value(self.value)

            @override
            def addressing_mode(self) -> AddressingMode:
                return AddressingMode.INDEX_X

        @dataclass(frozen=True)
        class IndexY(Arg):
            value: str | Word

            @override
            def bind(
                self,
                assembler: "assembler_lib.Assembler",
            ) -> "assembler_lib.Assembler":
                match self.value:
                    case str():
                        return assembler.with_ref(self.value)
                    case Word():
                        return assembler.with_value(self.value)

            @override
            def addressing_mode(self) -> AddressingMode:
                return AddressingMode.INDEX_Y

        name: str
        arg: Optional[Arg] = None

        def with_arg(self, arg: Arg) -> "Program.Instruction":
            return replace(self, arg=arg)

        def _addressing_mode(self) -> AddressingMode:
            return (
                self.arg.addressing_mode()
                if self.arg is not None
                else AddressingMode.NONE
            )

        def _opcode(self, instruction_set: InstructionSet) -> Byte:
            if (
                instruction := instruction_set.instructions_by_name.get(self.name)
            ) is None:
                raise self._error(
                    f"Instruction {self.name} not found.",
                    self.InstructionNotFound,
                )
            addressing_mode = self._addressing_mode()
            if (
                mode := instruction.modes_by_addressing_mode.get(addressing_mode)
            ) is None:
                raise self._error(
                    f"Instruction {self.name} " f"does not support {addressing_mode=}.",
                    self.InstructionModeNotFound,
                )
            return mode.opcode

        @override
        def bind(
            self, assembler: "assembler_lib.Assembler"
        ) -> "assembler_lib.Assembler":
            assembler = assembler.with_value(self._opcode(assembler.instruction_set))
            if self.arg is not None:
                assembler = self.arg.bind(assembler)
            return assembler

    @dataclass(frozen=True)
    class At(Statement):
        position: Word

        @override
        def bind(
            self, assembler: "assembler_lib.Assembler"
        ) -> "assembler_lib.Assembler":
            return assembler.with_next_position(self.position)

    instruction_set: InstructionSet
    statements: list[Statement] = field(default_factory=list[Statement])

    @override
    def __repr__(self) -> str:
        return f"Program({self.statements})"

    def with_statement(self, statement: Statement) -> "Program":
        return replace(self, statements=self.statements + [statement])

    def with_values(self, values: Iterable[Byte]) -> "Program":
        return self.with_statement(self.Literal(list(values)))

    def with_value(self, value: Byte | Word) -> "Program":
        match value:
            case Byte():
                return self.with_values([value])
            case Word():
                return self.with_values(value.to_bytes())

    def with_label(self, name: str) -> "Program":
        return self.with_statement(Program.Label(name))

    def with_ref(self, name: str) -> "Program":
        return self.with_statement(Program.Ref(name))

    def at_position(self, position: Word) -> "Program":
        return self.with_statement(Program.At(position))

    def assemble(self) -> "assembler_lib.Assembler.Output":
        return assembler_lib.Assembler.for_program(self).assemble()


from flip.programs import assembler as assembler_lib
