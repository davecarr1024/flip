from typing import Optional, override

from flip.components import Bus, Component, Counter, Register
from flip.components.controller import Assembler, InstructionSet


class Controller(Component):
    def __init__(
        self,
        instruction_set: InstructionSet,
        bus: Bus,
        name: Optional[str] = None,
        parent: Optional[Component] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.__step_counter = Counter(
            name="step_counter",
            parent=self,
            bus=bus,
        )
        self.__instruction_buffer = Register(
            name="instruction_buffer",
            parent=self,
            bus=bus,
        )
        self.__instruction_memory = Assembler(
            instruction_set=instruction_set,
        ).assemble()

    @override
    def tick_control(self) -> None:
        super().tick_control()
        self.__step_counter.increment = True
        opcode = self.__instruction_buffer.value
        statuses = {status.path: status.value for status in self.root.statuses}
        step_index = self.__step_counter.value
        controls = self.__instruction_memory.get(
            opcode=opcode,
            statuses=statuses,
            step_index=step_index,
        )
        for control in self.root.controls:
            control.value = control.path in controls
