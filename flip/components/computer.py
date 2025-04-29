from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Iterable, Mapping, Optional, Self

from flip.bytes import Byte, Word
from flip.components.alu import Alu
from flip.components.alu.operations import (
    Adc,
    And,
    Operation,
    OperationSet,
    Or,
    Rol,
    Ror,
    Sbc,
    Shl,
    Shr,
    Xor,
)
from flip.components.bus import Bus
from flip.components.component import Component
from flip.components.control import Control
from flip.components.controller.controller import Controller
from flip.components.memory import Memory
from flip.components.program_counter import ProgramCounter
from flip.components.register import Register
from flip.components.word_register import WordRegister
from flip.instructions import InstructionSet, InstructionSetBuilder
from flip.programs import Program, ProgramBuilder


class Computer(Component, ABC):
    @dataclass(frozen=True, kw_only=True)
    class InstructionSetBuilder(InstructionSetBuilder):
        alu_operation_set: OperationSet

        def _alu_operation(self, operation: str | Operation) -> Self:
            """Runs an ALU operation."""
            return self.step(
                *[
                    f"alu.{control}"
                    for control in Alu.encode_opcode_controls(
                        self.alu_operation_set,
                        operation,
                    )
                ]
            )

        def alu_operation(
            self,
            *,
            operation: str | Operation,
            out: str,
            lhs: str,
            rhs: Optional[str] = None,
        ) -> Self:
            """Runs an ALU operation.

            lhs is a byte register, and the byte is written to alu.lhs.
            rhs is an optional byte register, and the byte is written to alu.rhs.
            operation is the operation to perform.
            out is a byte register, and the result is written to it.
            """
            self = self.transfer_byte(lhs, "alu.lhs")
            if rhs is not None:
                self = self.transfer_byte(rhs, "alu.rhs")
            self = self._alu_operation(operation)
            return self.transfer_byte("alu.output", out)

        def transfer_byte(self, from_: str, to: str) -> Self:
            return self.step(f"{from_}.write", f"{to}.read")

        def transfer_word(self, from_: str, to: str) -> Self:
            return self.transfer_byte(f"{from_}.low", f"{to}.low").transfer_byte(
                f"{from_}.high", f"{to}.high"
            )

    @classmethod
    def _instruction_set_builder(cls) -> InstructionSetBuilder:
        return cls.InstructionSetBuilder(alu_operation_set=cls._alu_operation_set())

    @classmethod
    @abstractmethod
    def instruction_set(cls) -> InstructionSet:
        """Return the instruction set for this computer."""

    @classmethod
    def _alu_operation_set(cls) -> OperationSet:
        return OperationSet.create(
            {
                Adc(),
                And(),
                Or(),
                Rol(),
                Ror(),
                Sbc(),
                Shl(),
                Shr(),
                Xor(),
            }
        )

    def __init__(
        self,
        name: Optional[str] = None,
        children: Optional[Iterable[Component]] = None,
        data: Optional[Mapping[Word, Byte] | Program | ProgramBuilder] = None,
    ) -> None:
        super().__init__(name=name, children=children)
        self.__bus = Bus(name="bus", parent=self)
        self.__memory = Memory(
            name="memory",
            bus=self.__bus,
            parent=self,
        )
        self.__program_counter = ProgramCounter(
            name="program_counter", bus=self.__bus, parent=self
        )
        self.__controller = Controller(
            name="controller",
            bus=self.__bus,
            instruction_set=self.instruction_set(),
            parent=self,
        )
        self.__alu = Alu(
            name="alu",
            bus=self.__bus,
            operation_set=self._alu_operation_set(),
            parent=self,
        )
        self.__halt = Control(name="halt", parent=self, auto_clear=False)
        if data is not None:
            self.load(data)

    @property
    def halt(self) -> bool:
        return self.__halt.value

    @halt.setter
    def halt(self, value: bool) -> None:
        self.__halt.value = value

    def tick_until_halt(self) -> None:
        while not self.halt:
            self.tick()

    def _create_register(self, name: str) -> Register:
        return Register(name=name, bus=self.__bus, parent=self)

    def _create_word_register(self, name: str) -> WordRegister:
        return WordRegister(name=name, bus=self.__bus, parent=self)

    @property
    def memory(self) -> Memory:
        return self.__memory

    @property
    def alu(self) -> Alu:
        return self.__alu

    @property
    def program_counter(self) -> ProgramCounter:
        return self.__program_counter

    def load(self, data: Mapping[Word, Byte] | Program | ProgramBuilder) -> None:
        self._log(f"loading data {data}")
        match data:
            case Program():
                self.memory.load(data.assemble().memory)
            case ProgramBuilder():
                self.memory.load(data.build().assemble().memory)
            case _:
                self.memory.load(data)

    def run(self, program: Program | ProgramBuilder) -> None:
        self.load(program)
        self.tick_until_halt()
