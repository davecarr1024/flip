from abc import ABC, abstractmethod
from typing import Iterable, Mapping, Optional

from flip.bytes import Byte, Word
from flip.components.alu import Alu
from flip.components.alu.operations import (
    Adc,
    And,
    OperationSet,
    Or,
    Rol,
    Ror,
    Sbc,
    Shl,
    Shr,
    Xor,
)
from flip.components.alu.operations import Operation as AluOperation
from flip.components.bus import Bus
from flip.components.component import Component
from flip.components.control import Control
from flip.components.controller.controller import Controller
from flip.components.memory import Memory
from flip.components.program_counter import ProgramCounter
from flip.components.register import Register
from flip.components.result_analyzer import ResultAnalyzer
from flip.components.word_register import WordRegister
from flip.instructions import InstructionSet
from flip.programs import Program, ProgramBuilder


class Computer(Component, ABC):
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

    @classmethod
    def _encode_alu_opcode_controls(
        cls,
        operation: str | AluOperation,
        alu_path: str = "alu",
    ) -> frozenset[str]:
        return frozenset(
            f"{alu_path}.{control}"
            for control in Alu.encode_opcode_controls(
                cls._alu_operation_set(), operation
            )
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
        self.__result_analyzer = ResultAnalyzer(
            name="result_analyzer",
            bus=self.__bus,
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

    @property
    def controller(self) -> Controller:
        return self.__controller

    def load(self, data: Mapping[Word, Byte] | Program | ProgramBuilder) -> None:
        self._log(f"loading data {data}")
        match data:
            case Program():
                data_ = data.assemble().memory
            case ProgramBuilder():
                data_ = data.build().assemble().memory
            case _:
                data_ = data
        self._log(f"loading memory {data_}")
        self.memory.load(data_)

    def run(self, program: Program | ProgramBuilder) -> None:
        self.load(program)
        self.tick_until_halt()
