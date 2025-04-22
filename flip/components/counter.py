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
        self.__increment_enable = Control(name="increment_enable", parent=self)
        self.__reset_enable = Control(name="reset_enable", parent=self)

    @property
    def increment_enable(self) -> bool:
        return self.__increment_enable.value

    @increment_enable.setter
    def increment_enable(self, value: bool) -> None:
        self.__increment_enable.value = value

    @property
    def reset_enable(self) -> bool:
        return self.__reset_enable.value

    @reset_enable.setter
    def reset_enable(self, value: bool) -> None:
        self.__reset_enable.value = value

    @override
    def tick_process(self) -> None:
        super().tick_process()
        if self.reset_enable:
            self.value = 0
        if self.increment_enable:
            self.value += 1
