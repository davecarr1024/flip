from typing import Callable, Iterable, Mapping, Optional, Self, Union, override

from flip.bytes import Byte, Word
from flip.components.component import Component
from flip.components.computer import Computer
from flip.components.register import Register
from flip.instructions import InstructionImpl, InstructionMode, InstructionSet, Step
from flip.programs import Program, ProgramBuilder

type _ApplyOperand = Union[
    InstructionMode.Builder,
    InstructionImpl.Builder,
    Step.Builder,
]
type _ApplyResult = InstructionImpl.Builder
type _Apply = Callable[[_ApplyOperand], _ApplyResult]


class MinimalComputer(Computer):

    @override
    @classmethod
    def instruction_set(cls) -> InstructionSet:
        def transfer_byte(from_: str, to: str) -> _Apply:
            """Transfer a byte from one byte register to another."""
            return lambda builder: (
                builder.step(
                    f"{from_}.write",
                    f"{to}.read",
                )
            )

        def transfer_word(from_: str, to: str) -> _Apply:
            """Transfer a word from one word register to another."""
            return lambda builder: (
                builder
                # transfer low byte
                .apply(
                    transfer_byte(
                        f"{from_}.low",
                        f"{to}.low",
                    ),
                )
                # transfer high byte
                .apply(
                    transfer_byte(
                        f"{from_}.high",
                        f"{to}.high",
                    ),
                )
            )

        def load_immediate(to: str) -> _Apply:
            """Load the next program byte into a byte register."""
            return lambda builder: (
                builder
                # load pc to memory.address
                .apply(
                    transfer_word(
                        "program_counter",
                        "memory.address",
                    ),
                )
                # load byte from memory to {to} and inc pc
                .step(
                    "memory.write",
                    f"{to}.read",
                    "program_counter.increment",
                )
            )

        def load_word_at_pc(to: str, buffer: str = "arg_buffer.low") -> _Apply:
            """Load the next two program bytes into a word register."""
            return lambda builder: (
                builder
                # copy low byte to {buffer}
                .apply(load_immediate(buffer))
                # copy high byte to {to}.high
                .apply(load_immediate(f"{to}.high"))
                # copy low byte to {to}.low
                .apply(transfer_byte(buffer, f"{to}.low"))
            )

        def load_absolute(to: str, buffer: str = "arg_buffer.low") -> _Apply:
            """Load a byte from memory at the address from the next two program bytes"""
            return lambda builder: (
                builder
                # Load address at pc to memory.address
                .apply(load_word_at_pc("memory.address", buffer=buffer))
                # Load byte at memory.address to {to}
                .apply(transfer_byte("memory", to))
            )

        def alu_opcode(op: str) -> _Apply:
            return lambda builder: builder.step(*cls._encode_alu_opcode_controls(op))

        def a_alu_operation(op: str) -> _Apply:
            """Run an ALU operation with the accumulator as the lhs operand.

            Note that this assumes that this is either a unary operation that
            ignores alu.rhs, or that alu.rhs is already loaded with the rhs operand.
            """
            return lambda builder: (
                builder
                # a -> alu.lhs
                .apply(transfer_byte("a", "alu.lhs"))
                # run alu operation
                .apply(alu_opcode(op))
                # alu.output -> a
                .apply(transfer_byte("alu.output", "a"))
            )

        def a_alu_operation_immediate(op: str) -> _Apply:
            """Run an accumulator-based ALU operation with immediate addressing.

            alu.lhs comes from the accumulator.
            alu.rhs comes from the next program byte.
            The result is written back to the accumulator.
            """
            return lambda builder: (
                builder
                # Load next byte at pc to rhs.
                .apply(load_immediate("alu.rhs"))
                # Run ALU operation.
                .apply(a_alu_operation(op))
            )

        def a_alu_operation_absolute(op: str) -> _Apply:
            """Run an accumulator-based ALU operation with absolute addressing.

            alu.lhs comes from the accumulator.
            alu.rhs comes from the byte at the address from the next two program bytes.
            The result is written back to the accumulator.
            """
            return lambda builder: (
                builder
                # Load byte from memory at address at pc to rhs.
                .apply(load_absolute("alu.rhs"))
                # Run ALU operation.
                .apply(a_alu_operation(op))
            )

        return (
            InstructionSet.Builder()
            .instruction("nop")
            .mode("none")
            .step()
            .instruction("hlt")
            .mode("none")
            .step("halt")
            .instruction("tax")
            .mode("none")
            .apply(transfer_byte("a", "x"))
            .instruction("txa")
            .mode("none")
            .apply(transfer_byte("x", "a"))
            .instruction("tay")
            .mode("none")
            .apply(transfer_byte("a", "y"))
            .instruction("tya")
            .mode("none")
            .apply(transfer_byte("y", "a"))
            .instruction("lda")
            .mode("immediate")
            .apply(load_immediate("a"))
            .mode("absolute")
            .apply(load_absolute("a"))
            .mode("zero_page")
            .apply(load_immediate("memory.address.low"))
            .step("memory.address.high.reset")
            .apply(transfer_byte("memory", "a"))
            .instruction("jmp")
            .mode("absolute")
            .apply(load_word_at_pc("program_counter"))
            .instruction("sec")
            .mode("none")
            .step("alu.carry_in")
            .instruction("clc")
            .mode("none")
            .step("alu.carry_in.clear")
            .instruction("adc")
            .mode("immediate")
            .apply(a_alu_operation_immediate("adc"))
            .mode("absolute")
            .apply(a_alu_operation_absolute("adc"))
            .header()
            .step(
                "program_counter.low.write",
                "memory.address.low.read",
            )
            .step(
                "program_counter.high.write",
                "memory.address.high.read",
            )
            .step(
                "program_counter.increment",
                "memory.write",
                "controller.instruction_buffer.read",
            )
            .build()
            .with_last_step_controls("controller.step_counter.reset")
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
