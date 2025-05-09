from typing import Optional, override

from flip.bytes import Byte
from flip.components.bus import Bus
from flip.components.component import Component
from flip.components.control import Control
from flip.components.word_register import WordRegister


class StackPointer(WordRegister):
    def __init__(
        self,
        /,
        bus: Bus,
        name: str,
        high_value: Byte,
        low_value: Optional[Byte] = None,
        parent: Optional[Component] = None,
    ) -> None:
        super().__init__(
            bus=bus,
            name=name,
            low_value=low_value,
            high_value=high_value,
            parent=parent,
        )
        self.__increment = Control(name="increment", parent=self)
        self.__decrement = Control(name="decrement", parent=self)

    @property
    def increment(self) -> bool:
        return self.__increment.value

    @increment.setter
    def increment(self, value: bool) -> None:
        self.__increment.value = value

    @property
    def decrement(self) -> bool:
        return self.__decrement.value

    @decrement.setter
    def decrement(self, value: bool) -> None:
        self.__decrement.value = value

    @override
    def _tick_process(self) -> None:
        super()._tick_process()
        if self.increment:
            self.low = Byte(self.low.unsigned_value + 1)
        if self.decrement:
            self.low = Byte(self.low.unsigned_value - 1)
