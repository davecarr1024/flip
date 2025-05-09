from typing import Optional

from flip.bytes import Byte, Word
from flip.components.bus import Bus
from flip.components.component import Component
from flip.components.register import Register


class WordRegister(Component):
    def __init__(
        self,
        bus: Bus,
        name: str,
        parent: Optional[Component] = None,
        low_value: Optional[Byte] = None,
        high_value: Optional[Byte] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.__low = Register(
            name="low",
            parent=self,
            bus=bus,
            value=low_value,
        )
        self.__high = Register(
            name="high",
            parent=self,
            bus=bus,
            value=high_value,
        )

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
        return Word.from_bytes(self.__low.value, self.__high.value)

    @value.setter
    def value(self, value: Word) -> None:
        self.__low.value, self.__high.value = value.to_bytes()
