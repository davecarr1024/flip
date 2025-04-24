from typing import Optional, override

from flip.bytes import Byte
from flip.components import component
from flip.components.bus import Bus
from flip.components.control import Control
from flip.components.register import Register


class Counter(Register):
    def __init__(
        self,
        name: str,
        bus: Bus,
        parent: Optional[component.Component] = None,
    ) -> None:
        super().__init__(name=name, bus=bus, parent=parent)
        self.__increment = Control(name="increment", parent=self)

    @property
    def increment(self) -> bool:
        return self.__increment.value

    @increment.setter
    def increment(self, value: bool) -> None:
        self.__increment.value = value

    @override
    def _tick_process(self) -> None:
        if self.reset:
            self.value = Byte(0)
            self._log(f"reset to {self.value}")
        elif self.increment:
            self.value = self.value.add(Byte(1)).value
            self._log(f"incremented to {self.value}")
