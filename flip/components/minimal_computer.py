from typing import Callable, Iterable, Optional

from flip.components.component import Component
from flip.components.computer import Computer
from flip.components.register import Register
from flip.instructions import InstructionSet, InstructionSetBuilder


class MinimalComputer(Computer):
    def __init__(
        self,
        name: Optional[str] = None,
        children: Optional[Iterable[Component]] = None,
    ) -> None:
        def load_byte(
            from_low: str,
            from_high: str,
            to: str,
        ) -> Callable[[InstructionSetBuilder], InstructionSetBuilder]:
            """Copy a byte from memory to a byte register."""

            def impl(builder: InstructionSetBuilder) -> InstructionSetBuilder:
                return (
                    builder
                    # copy low address byte to memory.address_low
                    .step(from_low, "memory.address_low.read")
                    # copy high address byte to memory.address_high
                    .step(from_high, "memory.address_high.read")
                    # read byte from memory to {to}
                    .step("memory.write", to)
                )

            return impl

        def load_byte_at_pc(
            to: str,
        ) -> Callable[[InstructionSetBuilder], InstructionSetBuilder]:
            """Copy the next byte at pc to a byte register."""

            def impl(builder: InstructionSetBuilder) -> InstructionSetBuilder:
                return (
                    builder
                    # load byte from memory at program counter to {to}
                    .apply(
                        load_byte(
                            "program_counter.low.write",
                            "program_counter.high.write",
                            to,
                        )
                    )
                    # increment program counter
                    .step("program_counter.increment")
                )

            return impl

        def load_word_at_pc(
            to: str,
            buffer: str = "arg_buffer.low",
        ) -> Callable[[InstructionSetBuilder], InstructionSetBuilder]:
            """Copy the next two bytes at pc to a word register."""

            def impl(builder: InstructionSetBuilder) -> InstructionSetBuilder:
                return (
                    builder
                    # copy low byte to {buffer}
                    .apply(load_byte_at_pc(f"{buffer}.read"))
                    # copy high byte to {to}.high
                    .apply(load_byte_at_pc(f"{to}.high.read"))
                    # copy low byte to {to}.low
                    .step("arg_buffer.low.write", f"{to}.low.read")
                )

            return impl

        super().__init__(
            name=name,
            children=children,
            instruction_set=(
                (
                    InstructionSet.builder()
                    .instruction("nop", 0x00)
                    .step()
                    .instruction("hlt", 0x01)
                    .step("halt")
                    .instruction("tax", 0x02)
                    .step("a.write", "x.read")
                    .instruction("txa", 0x03)
                    .step("x.write", "a.read")
                    .instruction("tay", 0x04)
                    .step("a.write", "y.read")
                    .instruction("tya", 0x05)
                    .step("y.write", "a.read")
                    .instruction("lda")
                    .mode("immediate", 0x06)
                    .apply(load_byte_at_pc("a.read"))
                    .mode("absolute", 0x07)
                    .apply(load_byte_at_pc("arg_buffer.low.read"))
                    .apply(load_byte_at_pc("arg_buffer.high.read"))
                    .apply(
                        load_byte(
                            "arg_buffer.low.write",
                            "arg_buffer.high.write",
                            "a.read",
                        )
                    )
                    .mode("zero_page", 0x08)
                    .apply(load_byte_at_pc("memory.address_low.read"))
                    .step("memory.address_high.reset")
                    .step("memory.write", "a.read")
                    .instruction("jmp")
                    .mode("absolute", 0x20)
                    .apply(load_word_at_pc("program_counter"))
                    .header(
                        [
                            "program_counter.low.write",
                            "memory.address_low.read",
                        ],
                        [
                            "program_counter.high.write",
                            "memory.address_high.read",
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
            ),
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
