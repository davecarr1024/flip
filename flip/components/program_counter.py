from typing import Optional, override

from flip.bytes import Word
from flip.components.bus import Bus
from flip.components.component import Component
from flip.components.control import Control
from flip.components.word_register import WordRegister


class ProgramCounter(WordRegister):
    def __init__(
        self,
        bus: Bus,
        name: Optional[str] = None,
        parent: Optional[Component] = None,
    ) -> None:
        super().__init__(bus=bus, name=name, parent=parent)
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
    def _tick_process(self) -> None:
        if self.reset:
            self.value = Word(0)
            self._log(f"reset to {self.value}")
        elif self.increment:
            self.value = Word(self.value.value + 1)
            self._log(f"incremented to {self.value}")
