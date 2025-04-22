from typing import Optional, override

from flip.components import component
from flip.components.bus import Bus
from flip.components.control import Control


class Register(component.Component):
    class Error(component.Component.Error): ...

    class ReadError(Error, RuntimeError): ...

    def __init__(
        self,
        name: str,
        bus: Bus,
        parent: Optional[component.Component] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.__bus = bus
        self.__value: int = 0
        self.__write_enable = Control(name="write_enable", parent=self)
        self.__read_enable = Control(name="read_enable", parent=self)

    @property
    def bus(self) -> Bus:
        return self.__bus

    @property
    def value(self) -> int:
        return self.__value

    @value.setter
    def value(self, value: int) -> None:
        self.__value = value

    @property
    def write_enable(self) -> bool:
        return self.__write_enable.value

    @write_enable.setter
    def write_enable(self, value: bool) -> None:
        self.__write_enable.value = value

    @property
    def read_enable(self) -> bool:
        return self.__read_enable.value

    @read_enable.setter
    def read_enable(self, value: bool) -> None:
        self.__read_enable.value = value

    @override
    def tick_write(self) -> None:
        super().tick_write()
        if self.write_enable:
            self.bus.set(self.value, self)

    @override
    def tick_read(self) -> None:
        super().tick_read()
        if self.read_enable:
            if (value := self.bus.value) is None:
                raise self._error(f"Reading open bus on {self.path}.", self.ReadError)
            self.value = value
