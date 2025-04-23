from typing import Optional, override

from flip.bytes import Byte, Word
from flip.components.bus import Bus
from flip.components.component import Component
from flip.components.control import Control
from flip.components.register import Register


class ProgramCounter(Component):
    def __init__(
        self,
        bus: Bus,
        name: Optional[str] = None,
        parent: Optional[Component] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.__low = Register(name="low", parent=self, bus=bus)
        self.__high = Register(name="high", parent=self, bus=bus)
        self.__increment = Control(name="increment", parent=self)
        self.__reset = Control(name="reset", parent=self)

    @property
    def low(self) -> Byte:
        return self.__low.value

    @low.setter
    def low(self, value: Byte) -> None:
        self.__low.value = value

    @property
    def high(self) -> Byte:
        return self.__high.value

    @high.setter
    def high(self, value: Byte) -> None:
        self.__high.value = value

    @property
    def value(self) -> Word:
        return Word.from_bytes(self.low, self.high)

    @value.setter
    def value(self, value: Word) -> None:
        self.low, self.high = value.to_bytes()

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
    def _tick_process(self) -> None:
        if self.reset:
            self.value = Word(0)
            self._log(f"reset to {self.value}")
        elif self.increment:
            self.value = Word(self.value.value + 1)
            self._log(f"incremented to {self.value}")
