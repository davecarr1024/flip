from typing import Optional, override

from flip.components.bus import Bus
from flip.components.component import Component
from flip.components.register import Register
from flip.components.status import Status


class ResultAnalyzer(Register):
    def __init__(
        self,
        name: str,
        bus: Bus,
        parent: Optional[Component] = None,
    ) -> None:
        super().__init__(
            name=name,
            bus=bus,
            parent=parent,
        )

        self.__zero = Status(
            name="zero",
            parent=self,
        )
        self.__negative = Status(
            name="negative",
            parent=self,
        )

    @property
    def zero(self) -> bool:
        return self.__zero.value

    @property
    def negative(self) -> bool:
        return self.__negative.value

    @override
    def _tick_process(self) -> None:
        super()._tick_process()
        value = self.value.unsigned_value
        self.__zero.value = value == 0
        self.__negative.value = value & 0x80 != 0
