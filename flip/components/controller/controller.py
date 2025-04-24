from typing import Optional, override

from flip.components.bus import Bus
from flip.components.component import Component
from flip.components.controller.assembler import Assembler
from flip.components.counter import Counter
from flip.components.register import Register
from flip.instructions import InstructionSet


class Controller(Component):
    class Error(Component.Error): ...

    class KeyError(Error, Component.KeyError, KeyError): ...

    class MissingStatusError(KeyError): ...

    class MissingControlError(KeyError): ...

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
    def _tick_control(self) -> None:
        opcode = self.__instruction_buffer.value
        for status_path in self.__instruction_memory.format.statuses:
            if status_path not in self.root.statuses_by_path:
                raise self._error(
                    f"Instruction status {status_path} not found in root statuses.",
                    self.MissingStatusError,
                )
        statuses = {status.path: status.value for status in self.root.statuses}
        step_index = self.__step_counter.value
        control_paths = self.__instruction_memory.get(
            opcode=opcode,
            statuses=statuses,
            step_index=step_index,
        )
        for control_path in control_paths:
            if control_path not in self.root.controls_by_path:
                raise self._error(
                    f"Control {control_path} not found in root controls.",
                    self.MissingControlError,
                )
        for control in self.root.controls:
            control.value = control.path in control_paths
        self.__step_counter.increment = True
        self._log(
            f"opcode = {opcode}, "
            f"statuses = {statuses}, "
            f"step_index = {step_index}, "
            f"controls = {control_paths}"
        )
