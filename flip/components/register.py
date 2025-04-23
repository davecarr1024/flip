from typing import Optional, override

from flip.bytes import Byte
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
        self.__value = Byte(0)
        self.__write = Control(name="write", parent=self)
        self.__read = Control(name="read", parent=self)

    @property
    def bus(self) -> Bus:
        return self.__bus

    @property
    def value(self) -> Byte:
        return self.__value

    @value.setter
    def value(self, value: Byte) -> None:
        self.__value = value

    @property
    def write(self) -> bool:
        return self.__write.value

    @write.setter
    def write(self, value: bool) -> None:
        self.__write.value = value

    @property
    def read(self) -> bool:
        return self.__read.value

    @read.setter
    def read(self, value: bool) -> None:
        self.__read.value = value

    @override
    def _tick_write(self) -> None:
        if self.write:
            print(f"{self.path} writing {self.value} to bus")
            self.bus.set(self.value, self)

    @override
    def _tick_read(self) -> None:
        if self.read:
            if (value := self.bus.value) is None:
                raise self._error(f"Reading open bus on {self.path}.", self.ReadError)
            print(f"{self.path} reading {value} from bus")
            self.value = value
