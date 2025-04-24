from typing import Iterable, Optional

from flip.components.bus import Bus
from flip.components.component import Component
from flip.components.control import Control
from flip.components.controller.controller import Controller
from flip.components.memory import Memory
from flip.components.program_counter import ProgramCounter
from flip.components.register import Register
from flip.components.word_register import WordRegister
from flip.instructions import InstructionSet


class Computer(Component):
    def __init__(
        self,
        instruction_set: InstructionSet,
        name: Optional[str] = None,
        children: Optional[Iterable[Component]] = None,
    ) -> None:
        super().__init__(name=name, children=children)
        self.__bus = Bus(name="bus", parent=self)
        self.__memory = Memory(name="memory", bus=self.__bus, parent=self)
        self.__program_counter = ProgramCounter(
            name="program_counter", bus=self.__bus, parent=self
        )
        self.__controller = Controller(
            name="controller",
            bus=self.__bus,
            instruction_set=instruction_set,
            parent=self,
        )
        self.__halt = Control(name="halt", parent=self, auto_clear=False)

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
    def program_counter(self) -> ProgramCounter:
        return self.__program_counter
