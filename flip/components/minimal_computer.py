from typing import Iterable, Optional

from flip.bytes import Byte
from flip.components.component import Component
from flip.components.computer import Computer
from flip.components.controller.instruction import Instruction
from flip.components.controller.instruction_set import InstructionSet
from flip.components.controller.step import Step
from flip.components.register import Register


class MinimalComputer(Computer):
    def __init__(
        self,
        name: Optional[str] = None,
        children: Optional[Iterable[Component]] = None,
    ) -> None:
        super().__init__(
            name=name,
            children=children,
            instruction_set=InstructionSet.create(
                instructions={
                    Instruction.create(
                        name="nop",
                        opcode=Byte(0x00),
                        steps=[],
                    ),
                    Instruction.create(
                        name="hlt",
                        opcode=Byte(0x01),
                        steps=[
                            Step.create({"halt"}),
                        ],
                    ),
                    Instruction.create(
                        name="tax",
                        opcode=Byte(0x02),
                        steps=[
                            Step.create(["a.write", "x.read"]),
                        ],
                    ),
                    Instruction.create(
                        name="txa",
                        opcode=Byte(0x03),
                        steps=[
                            Step.create(["x.write", "a.read"]),
                        ],
                    ),
                    Instruction.create(
                        name="tay",
                        opcode=Byte(0x04),
                        steps=[
                            Step.create(["a.write", "y.read"]),
                        ],
                    ),
                    Instruction.create(
                        name="tya",
                        opcode=Byte(0x05),
                        steps=[
                            Step.create(["y.write", "a.read"]),
                        ],
                    ),
                }
            )
            .with_header(
                [
                    Step.create(
                        [
                            "program_counter.low.write",
                            "memory.address_low.read",
                        ]
                    ),
                    Step.create(
                        [
                            "program_counter.high.write",
                            "memory.address_high.read",
                        ]
                    ),
                    Step.create(
                        [
                            "program_counter.increment",
                            "memory.write",
                            "controller.instruction_buffer.read",
                        ]
                    ),
                ]
            )
            .with_footer(
                [
                    Step.create(["controller.step_counter.reset"]),
                ]
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
