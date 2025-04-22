from typing import Optional, override

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
        self.__enable_increment = Control(name="enable_increment", parent=self)
        self.__enable_reset = Control(name="enable_reset", parent=self)

    @property
    def enable_increment(self) -> bool:
        return self.__enable_increment.value

    @enable_increment.setter
    def enable_increment(self, value: bool) -> None:
        self.__enable_increment.value = value

    @property
    def enable_reset(self) -> bool:
        return self.__enable_reset.value

    @enable_reset.setter
    def enable_reset(self, value: bool) -> None:
        self.__enable_reset.value = value

    @override
    def tick_process(self) -> None:
        super().tick_process()
        if self.enable_reset:
            self.value = 0
        if self.enable_increment:
            self.value += 1
