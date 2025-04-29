from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Self, override

from flip.bytes import Byte, Word
from flip.components.alu.operations import Operation
from flip.components.component import Component
from flip.components.computer import Computer
from flip.components.register import Register
from flip.instructions import InstructionSet
from flip.programs import Program, ProgramBuilder


class MinimalComputer(Computer):
    @dataclass(frozen=True)
    class InstructionSetBuilder(Computer.InstructionSetBuilder):
        def load_byte_from_register_address(
            self,
            from_: str,
            to: str,
        ) -> Self:
            """Copy a byte from memory at {from} to a byte register.

            {from} is a word register, and the address is read from it.
            {to} is a byte register, and the byte is written to it.
            """

            return (
                self
                # Copy the address from {from} to memory.address.
                .transfer_word(from_, "memory.address")
                # Read the byte from memory to {to}.
                .transfer_byte("memory", to)
            )

        def load_byte_at_pc(
            self,
            to: str,
        ) -> Self:
            """Copy the next byte in memory at {pc} to a byte register.

            {to} is a byte register, and the byte is written to it.
            """

            return (
                self
                # load byte from memory at program counter to {to}
                .load_byte_from_register_address(
                    "program_counter",
                    to,
                )
                # increment program counter
                .step("program_counter.increment")
            )

        def load_word_at_pc(
            self,
            to: str,
            buffer: str = "arg_buffer.low",
        ) -> Self:
            """Copy the two bytes in memory at {pc} to a word register.

            {to} is a word register, and the bytes are written to it.
            {buffer} is a byte register, and the first byte is written to it.
            """

            return (
                self
                # copy low byte to {buffer}
                .load_byte_at_pc(buffer)
                # copy high byte to {to}.high
                .load_byte_at_pc(f"{to}.high")
                # copy low byte to {to}.low
                .transfer_byte(buffer, f"{to}.low")
            )

        def load_byte_from_pc_address(
            self,
            to: str,
            buffer: str = "arg_buffer.low",
        ) -> Self:
            """Indirectly load a byte from memory using the address at {pc}."""
            return (
                self
                # Load address at pc to memory.address
                .load_word_at_pc("memory.address", buffer=buffer)
                # Load byte at memory.address to {to}
                .transfer_byte("memory", to)
            )

        def _a_alu_operation(self, operation: Operation | str) -> Self:
            """Define an accumulator-based ALU operation.

            Note that this assumes that alu.rhs is already loaded with
            the rhs operand (if any) and that alu.lhs comes from the accumulator,
            and alu.output goes to the accumulator.
            """
            return (
                self.alu_operation(operation=operation, lhs="a", out="a")
                # # a -> alu.lhs
                # .transfer_byte("a", "alu.lhs")
                # # run alu operation
                # ._alu_operation(operation)
                # # alu.output -> a
                # .transfer_byte("alu.output","a")
            )

        def a_alu_operation_immediate(self, operation: Operation | str) -> Self:
            """Define an accumulator-based ALU operation with immediate addressing."""
            return (
                self
                # Load next byte at pc to rhs.
                .load_byte_at_pc("alu.rhs")
                # Run ALU operation.
                ._a_alu_operation(operation)
            )

        def a_alu_operation_absolute(self, operation: Operation | str) -> Self:
            """Define an accumulator-based ALU operation with absolute addressing."""
            return (
                self
                # Load byte from memory at address at pc to rhs.
                .load_byte_from_pc_address("alu.rhs")
                # Run ALU operation.
                ._a_alu_operation(operation)
            )

    @classmethod
    @override
    def _instruction_set_builder(cls) -> InstructionSetBuilder:
        return cls.InstructionSetBuilder(alu_operation_set=cls._alu_operation_set())

    @override
    @classmethod
    def instruction_set(cls) -> InstructionSet:
        return (
            cls._instruction_set_builder()
            .instruction("nop", 0x00)
            .step()
            .instruction("hlt", 0x01)
            .step("halt")
            .instruction("tax", 0x02)
            .transfer_byte("a", "x")
            .instruction("txa", 0x03)
            .transfer_byte("x", "a")
            .instruction("tay", 0x04)
            .transfer_byte("a", "y")
            .instruction("tya", 0x05)
            .transfer_byte("y", "a")
            .instruction("lda")
            .mode("immediate", 0x06)
            .load_byte_at_pc("a")
            .mode("absolute", 0x07)
            .load_byte_from_pc_address("a")
            .mode("zero_page", 0x08)
            .load_byte_at_pc("memory.address.low")
            .step("memory.address.high.reset")
            .transfer_byte("memory", "a")
            .instruction("jmp")
            .mode("absolute", 0x20)
            .load_word_at_pc("program_counter")
            .instruction("sec", 0x40)
            .step("alu.carry_in")
            .instruction("clc", 0x41)
            .step("alu.carry_in.clear")
            .instruction("adc")
            .mode("immediate", 0x42)
            .a_alu_operation_immediate("adc")
            .mode("absolute", 0x43)
            .a_alu_operation_absolute("adc")
            .header(
                [
                    "program_counter.low.write",
                    "memory.address.low.read",
                ],
                [
                    "program_counter.high.write",
                    "memory.address.high.read",
                ],
                [
                    "program_counter.increment",
                    "memory.write",
                    "controller.instruction_buffer.read",
                ],
            )
            .footer("controller.step_counter.reset")
            .build()
        )

    class _ProgramBuilder(ProgramBuilder):
        def nop(self) -> Self:
            return self.instruction("nop")

        def hlt(self) -> Self:
            return self.instruction("hlt")

        def tax(self) -> Self:
            return self.instruction("tax")

        def txa(self) -> Self:
            return self.instruction("txa")

        def tay(self) -> Self:
            return self.instruction("tay")

        def tya(self) -> Self:
            return self.instruction("tya")

        def lda(self, arg: int | Byte | str) -> Self:
            return self.instruction("lda", arg)

        def lda_zero_page(self, arg: int | Byte) -> Self:
            return self.instruction("lda").zero_page(arg)

        def jmp(self, arg: int | Word | str) -> Self:
            return self.instruction("jmp").absolute(arg)

        def sec(self) -> Self:
            return self.instruction("sec")

        def clc(self) -> Self:
            return self.instruction("clc")

        def adc(self, arg: int | Byte | str) -> Self:
            return self.instruction("adc", arg)

        def load(self) -> "MinimalComputer":
            return MinimalComputer(data=self.build())

        def run(self) -> "MinimalComputer":
            computer = self.load()
            computer.tick_until_halt()
            return computer

    @classmethod
    def program_builder(cls) -> _ProgramBuilder:
        return cls._ProgramBuilder.for_instruction_set(cls.instruction_set())

    def __init__(
        self,
        name: Optional[str] = None,
        children: Optional[Iterable[Component]] = None,
        data: Optional[Mapping[Word, Byte] | Program | ProgramBuilder] = None,
    ) -> None:
        super().__init__(
            name=name,
            children=children,
            data=data,
        )
        self.__a = self._create_register("a")
        self.__x = self._create_register("x")
        self.__y = self._create_register("y")
        self.__arg_buffer = self._create_word_register("arg_buffer")

    @property
    def a(self) -> Register:
        return self.__a

    @property
    def x(self) -> Register:
        return self.__x

    @property
    def y(self) -> Register:
        return self.__y
