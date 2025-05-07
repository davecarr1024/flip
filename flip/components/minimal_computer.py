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

        def load_indexed(
            to: str,
            index: str,
            buffer: str = "arg_buffer.low",
        ) -> _Apply:
            """Load a byte byte from an indexed location in memory.

            The next two program bytes are used as the base address.
            The index register is added to the low byte of the address, with
            a carry into the high byte.
            The result is loaded into {to}.
            """
            return lambda builder: (
                builder
                # Load low address-in byte to alu.lhs.
                .apply(load_immediate("alu.lhs"))
                # Load high address-in byte to buffer.
                .apply(load_immediate(buffer))
                # Clear carry in for the first add.
                .step("alu.carry_in.clear")
                # Add index to low address-in byte.
                .step(
                    f"{index}.write",
                    "alu.rhs.read",
                    *cls._encode_alu_opcode_controls("adc"),
                )
                # Copy result to memory.address.low.
                .apply(transfer_byte("alu.output", "memory.address.low"))
                # Prepare for rhs carry add.
                .step(
                    # Copy high address in byte to lhs.
                    f"{buffer}.write",
                    "alu.lhs.read",
                    # Latch carry state from the first add.
                    "controller.status.latch",
                    # Zero alu.rhs for the second add - just adding the carry.
                    "alu.rhs.reset",
                )
                # Add carry to high address-in byte.
                .step(*cls._encode_alu_opcode_controls("adc"))
                # Copy result to memory.address.high.
                .apply(transfer_byte("alu.output", "memory.address.high"))
                # Load byte at memory.address to {to}.
                .apply(transfer_byte("memory", to))
            )

        def load_zero_page(to: str) -> _Apply:
            """Load a byte at the next address, in the zero page."""
            return lambda builder: (
                builder
                # Load address at pc to memory.address.low
                .apply(load_immediate("memory.address.low"))
                # Reset memory.address.high
                .step("memory.address.high.reset")
                # Load byte at memory.address to {to}
                .apply(transfer_byte("memory", to))
            )

        def store_absolute(from_: str, buffer: str = "arg_buffer.low") -> _Apply:
            """Store a byte to memory at the address from the next two program bytes"""
            return lambda builder: (
                builder
                # Load address at pc to memory.address
                .apply(load_word_at_pc("memory.address", buffer=buffer))
                # Store byte at memory.address from {from_}
                .apply(transfer_byte(from_, "memory"))
            )

        def store_zero_page(from_: str) -> _Apply:
            """Store a byte to memory at the next address, in the zero page."""
            return lambda builder: (
                builder
                # Load address at pc to memory.address.low
                .apply(load_immediate("memory.address.low"))
                # Reset memory.address.high
                .step("memory.address.high.reset")
                # Store byte at memory.address from {from_}
                .apply(transfer_byte(from_, "memory"))
            )

        def a_alu_operation(op: str) -> _Apply:
            """Run an ALU operation with the accumulator as the lhs operand.

            Note that this assumes that this is either a unary operation that
            ignores alu.rhs, or that alu.rhs is already loaded with the rhs operand.
            """
            return lambda builder: (
                builder
                # a -> alu.lhs and run alu operation
                # Doing these on the same step is ok because the ALU will
                # load the lhs during tick_write/read, and then run the operation
                # during tick_process.
                .step(*cls._encode_alu_opcode_controls(op), "a.write", "alu.lhs.read")
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

        def conditional_jump(status: str, invert: bool = False) -> _Apply:
            """Conditionally jump to the address from the next two program bytes."""

            return lambda builder: (
                builder
                # If status is set, jump to address at pc.
                .impl(**{status: not invert})
                .apply(load_word_at_pc("program_counter"))
                # If status is not set, increment pc by 2.
                .impl(**{status: invert})
                .step("program_counter.increment")
                .step("program_counter.increment")
            )

        def transfer_instruction(
            builder: InstructionSet.Builder,
            name: str,
            from_: str,
            to_: str,
        ) -> InstructionSet.Builder:
            return (
                builder.instruction(name)
                .mode("none")
                .apply(transfer_byte(from_, to_))
                .end_instruction()
            )

        def load_instruction(
            builder: InstructionSet.Builder,
            name: str,
            to_: str,
            /,
            include_index_addressing_modes: bool = False,
        ) -> InstructionSet.Builder:
            instruction_builder = (
                builder.instruction(name)
                .mode("immediate")
                .apply(load_immediate(to_))
                .mode("absolute")
                .apply(load_absolute(to_))
                .mode("zero_page")
                .apply(load_zero_page(to_))
            )
            if include_index_addressing_modes:
                instruction_builder = (
                    instruction_builder.mode("index_x")
                    .apply(load_indexed(to_, "x"))
                    .mode("index_y")
                    .apply(load_indexed(to_, "y"))
                )
            return instruction_builder.end_instruction()

        def store_instruction(
            builder: InstructionSet.Builder, name: str, from_: str
        ) -> InstructionSet.Builder:
            return (
                builder.instruction(name)
                .mode("absolute")
                .apply(store_absolute(from_))
                .mode("zero_page")
                .apply(store_zero_page(from_))
                .end_instruction()
            )

        def load_and_store_instructions(
            builder: InstructionSet.Builder,
            reg: str,
            /,
            include_index_addressing_modes: bool = False,
        ) -> InstructionSet.Builder:
            assert len(reg) == 1
            builder = load_instruction(
                builder,
                f"ld{reg}",
                reg,
                include_index_addressing_modes=include_index_addressing_modes,
            )
            builder = store_instruction(builder, f"st{reg}", reg)
            return builder

        def alu_binary_instruction(
            builder: InstructionSet.Builder,
            name: str,
            op: Optional[str] = None,
        ) -> InstructionSet.Builder:
            op_ = op if op is not None else name
            return (
                builder.instruction(name)
                .mode("immediate")
                .apply(a_alu_operation_immediate(op_))
                .mode("absolute")
                .apply(a_alu_operation_absolute(op_))
                .end_instruction()
            )

        def alu_unary_instruction(
            builder: InstructionSet.Builder,
            name: str,
            op: Optional[str] = None,
        ) -> InstructionSet.Builder:
            op_ = op if op is not None else name
            return (
                builder.instruction(name)
                .mode("none")
                .apply(a_alu_operation(op_))
                .end_instruction()
            )

        def conditional_jump_instruction(
            builder: InstructionSet.Builder,
            name: str,
            invert_name: str,
            status: str,
        ) -> InstructionSet.Builder:
            return (
                builder.instruction(name)
                .mode("absolute")
                .apply(conditional_jump(status))
                .instruction(invert_name)
                .mode("absolute")
                .apply(conditional_jump(status, invert=True))
                .end_instruction()
            )

        builder: InstructionSet.Builder = InstructionSet.Builder()
        # nop - no operation
        builder = builder.instruction("nop").mode("none").step().end_instruction()
        # hlt - halt and catch fire
        builder = builder.instruction("hlt").mode("none").step("halt").end_instruction()

        # A X Y transfer instructions

        # tax - transfer accumulator to x
        builder = transfer_instruction(builder, "tax", "a", "x")
        # txa - transfer x to accumulator
        builder = transfer_instruction(builder, "txa", "x", "a")
        # tay - transfer accumulator to y
        builder = transfer_instruction(builder, "tay", "a", "y")
        # tya - transfer y to accumulator
        builder = transfer_instruction(builder, "tya", "y", "a")

        # A X Y load and store instructions

        # lda and sta - load and store accumulator
        builder = load_and_store_instructions(
            builder,
            "a",
            include_index_addressing_modes=True,
        )
        # ldx and stx - load and store x
        builder = load_and_store_instructions(builder, "x")
        # ldy and sty - load and store y
        builder = load_and_store_instructions(builder, "y")

        # jmp - jump to address
        builder = (
            builder.instruction("jmp")
            .mode("absolute")
            .apply(load_word_at_pc("program_counter"))
            .end_instruction()
        )

        # ALU instructions

        # sec - set carry
        builder = (
            builder.instruction("sec")
            .mode("none")
            .step("alu.carry_in")
            .end_instruction()
        )
        # clc - clear carry
        builder = (
            builder.instruction("clc")
            .mode("none")
            .step("alu.carry_in.clear")
            .end_instruction()
        )
        # adc - add with carry
        builder = alu_binary_instruction(builder, "adc")
        # sbc - subtract with carry
        builder = alu_binary_instruction(builder, "sbc")
        # and - and
        builder = alu_binary_instruction(builder, "and")
        # ora - or
        builder = alu_binary_instruction(builder, "ora", "or")
        # eor - exclusive or
        builder = alu_binary_instruction(builder, "eor", "xor")
        # asl - arithmetic shift left
        builder = alu_unary_instruction(builder, "asl", "shl")
        # lsr - logical shift right
        builder = alu_unary_instruction(builder, "lsr", "shr")
        # rol - rotate left
        builder = alu_unary_instruction(builder, "rol")
        # ror - rotate right
        builder = alu_unary_instruction(builder, "ror")
        # cmp - compare
        builder = (
            builder.instruction("cmp")
            .mode("immediate")
            # Load next byte at pc to rhs.
            .apply(load_immediate("alu.rhs"))
            # a -> alu.lhs and run alu operation
            # always set carry to ensure we don't borrow
            # discard sbc result
            .step(
                *cls._encode_alu_opcode_controls("sbc"),
                "a.write",
                "alu.lhs.read",
                "alu.carry_in",
            )
            .mode("absolute")
            # Load byte from memory at address at pc to rhs.
            .apply(load_absolute("alu.rhs"))
            # a -> alu.lhs and run alu operation
            # always set carry to ensure we don't borrow
            # discard sbc result
            .step(
                *cls._encode_alu_opcode_controls("sbc"),
                "a.write",
                "alu.lhs.read",
                "alu.carry_in",
            )
            .end_instruction()
        )

        # beq/bne - branch on zero flag
        builder = conditional_jump_instruction(builder, "beq", "bne", "alu.zero")
        # bmi/bpl - branch on negative flag
        builder = conditional_jump_instruction(builder, "bmi", "bpl", "alu.negative")
        # bcs/bcc - branch on carry flag
        builder = conditional_jump_instruction(builder, "bcs", "bcc", "alu.carry_out")
        # bvs/bvc - branch on overflow flag
        builder = conditional_jump_instruction(builder, "bvs", "bvc", "alu.overflow")

        # header - steps to run before every instruction
        instruction_set = (
            builder.header()
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
        )

        # footer - control to set during last step of every instruction
        instruction_set = instruction_set.with_last_step_controls(
            # reset the controller's step counter
            "controller.step_counter.reset",
            # latch the status register - this must be the last step
            # of every instruction because it gathers all the statuses
            # from the root component and latches them into the status
            # register, ready for the next instruction.
            "controller.status.latch",
        )
        return instruction_set

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

        def lda_index_x(self, arg: int | Word | str) -> Self:
            return self.instruction("lda").index_x(arg)

        def lda_index_y(self, arg: int | Word | str) -> Self:
            return self.instruction("lda").index_y(arg)

        def sta(self, arg: int | Word | str) -> Self:
            return self.instruction("sta").absolute(arg)

        def sta_zero_page(self, arg: int | Byte) -> Self:
            return self.instruction("sta").zero_page(arg)

        def ldx(self, arg: int | Byte | str) -> Self:
            return self.instruction("ldx", arg)

        def ldx_zero_page(self, arg: int | Byte) -> Self:
            return self.instruction("ldx").zero_page(arg)

        def stx(self, arg: int | Word | str) -> Self:
            return self.instruction("stx").absolute(arg)

        def stx_zero_page(self, arg: int | Byte) -> Self:
            return self.instruction("stx").zero_page(arg)

        def ldy(self, arg: int | Byte | str) -> Self:
            return self.instruction("ldy", arg)

        def ldy_zero_page(self, arg: int | Byte) -> Self:
            return self.instruction("ldy").zero_page(arg)

        def sty(self, arg: int | Word | str) -> Self:
            return self.instruction("sty").absolute(arg)

        def sty_zero_page(self, arg: int | Byte) -> Self:
            return self.instruction("sty").zero_page(arg)

        def jmp(self, arg: int | Word | str) -> Self:
            return self.instruction("jmp").absolute(arg)

        def sec(self) -> Self:
            return self.instruction("sec")

        def clc(self) -> Self:
            return self.instruction("clc")

        def adc(self, arg: int | Byte | str) -> Self:
            return self.instruction("adc", arg)

        def sbc(self, arg: int | Byte | str) -> Self:
            return self.instruction("sbc", arg)

        def and_(self, arg: int | Byte | str) -> Self:
            return self.instruction("and", arg)

        def ora(self, arg: int | Byte | str) -> Self:
            return self.instruction("ora", arg)

        def eor(self, arg: int | Byte | str) -> Self:
            return self.instruction("eor", arg)

        def asl(self) -> Self:
            return self.instruction("asl")

        def lsr(self) -> Self:
            return self.instruction("lsr")

        def rol(self) -> Self:
            return self.instruction("rol")

        def ror(self) -> Self:
            return self.instruction("ror")

        def cmp(self, arg: int | Byte | str) -> Self:
            return self.instruction("cmp", arg)

        def beq(self, arg: int | Word | str) -> Self:
            return self.instruction("beq").absolute(arg)

        def bne(self, arg: int | Word | str) -> Self:
            return self.instruction("bne").absolute(arg)

        def bmi(self, arg: int | Word | str) -> Self:
            return self.instruction("bmi").absolute(arg)

        def bpl(self, arg: int | Word | str) -> Self:
            return self.instruction("bpl").absolute(arg)

        def bcs(self, arg: int | Word | str) -> Self:
            return self.instruction("bcs").absolute(arg)

        def bcc(self, arg: int | Word | str) -> Self:
            return self.instruction("bcc").absolute(arg)

        def bvs(self, arg: int | Word | str) -> Self:
            return self.instruction("bvs").absolute(arg)

        def bvc(self, arg: int | Word | str) -> Self:
            return self.instruction("bvc").absolute(arg)

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
