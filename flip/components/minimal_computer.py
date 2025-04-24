from typing import Iterable, Optional

from flip.components.component import Component
from flip.components.computer import Computer
from flip.components.register import Register
from flip.instructions import InstructionSet


class MinimalComputer(Computer):
    def __init__(
        self,
        name: Optional[str] = None,
        children: Optional[Iterable[Component]] = None,
    ) -> None:
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
                    .step(
                        "program_counter.low.write",
                        "memory.address_low.read",
                    )
                    .step(
                        "program_counter.high.write",
                        "memory.address_high.read",
                    )
                    .step(
                        "memory.write",
                        "a.read",
                        "program_counter.increment",
                    )
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

    @property
    def a(self) -> Register:
        return self.__a

    @property
    def x(self) -> Register:
        return self.__x

    @property
    def y(self) -> Register:
        return self.__y
