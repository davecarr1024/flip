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
        self.__reset = Control(name="reset", parent=self)

    @property
    def increment(self) -> bool:
        return self.__increment.value

    @increment.setter
    def increment(self, value: bool) -> None:
        self.__increment.value = value

    @property
    def reset(self) -> bool:
        return self.__reset.value

    @reset.setter
    def reset(self, value: bool) -> None:
        self.__reset.value = value

    @override
    def tick_process(self) -> None:
        super().tick_process()
        print(f"\n{self.path} tick_process()")
        if self.increment:
            self.value = self.value.add(Byte(1)).value
            print(f"  {self.path} incremented to {self.value}")
        if self.reset:
            self.value = Byte(0)
            print(f"  {self.path} reset to {self.value}")
        print(f"/{self.path} tick_process()\n")
