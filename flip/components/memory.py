from typing import Iterator, Mapping, MutableMapping, Optional, override

from flip.bytes import Byte, Word
from flip.components.bus import Bus
from flip.components.component import Component
from flip.components.control import Control
from flip.components.register import Register


class Memory(Component, MutableMapping[Word, Byte]):
    class Error(Component.Error): ...

    class ReadError(Error, RuntimeError): ...

    class KeyError(Error, Component.KeyError, KeyError): ...

    def __init__(
        self,
        bus: Bus,
        data: Optional[Mapping[Word, Byte]] = None,
        name: Optional[str] = None,
        parent: Optional[Component] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.__bus = bus
        self.__write = Control(name="write", parent=self)
        self.__read = Control(name="read", parent=self)
        self.__high_reset = Control(name="high_reset", parent=self)
        self.__address_low = Register(name="address_low", bus=bus, parent=self)
        self.__address_high = Register(name="address_high", bus=bus, parent=self)
        self.__data: MutableMapping[Word, Byte] = (
            dict(data) if data is not None else dict()
        )

    @property
    def address(self) -> Word:
        return Word.from_bytes(self.__address_low.value, self.__address_high.value)

    @address.setter
    def address(self, value: Word) -> None:
        self.__address_low.value, self.__address_high.value = value.to_bytes()

    @property
    def value(self) -> Byte:
        return self.__data.get(self.address, Byte(0))

    @value.setter
    def value(self, value: Byte) -> None:
        self[self.address] = value

    @override
    def __len__(self) -> int:
        return len(self.__data)

    @override
    def __iter__(self) -> Iterator[Word]:
        yield from self.__data

    @override
    def __getitem__(self, address: Word) -> Byte:
        try:
            return self.__data[address]
        except KeyError as e:
            raise self._error(f"Address {address} not found.", self.KeyError) from e

    @override
    def __setitem__(self, address: Word, value: Byte) -> None:
        self.__data[address] = value

    @override
    def __delitem__(self, address: Word) -> None:
        try:
            del self.__data[address]
        except KeyError as e:
            raise self._error(f"Address {address} not found.", self.KeyError) from e

    @property
    def read(self) -> bool:
        return self.__read.value

    @read.setter
    def read(self, value: bool) -> None:
        self.__read.value = value

    @property
    def write(self) -> bool:
        return self.__write.value

    @write.setter
    def write(self, value: bool) -> None:
        self.__write.value = value

    @override
    def _tick_read(self) -> None:
        if self.read:
            if (value := self.__bus.value) is None:
                raise self._error("trying to read open bus", self.ReadError)
            self._log(f"reading {value} from bus to address {self.address}")
            self.value = value

    @override
    def _tick_write(self) -> None:
        if self.write:
            value = self.value
            self._log(f"writing {value} to bus from address {self.address}")
            self.__bus.set(value, self)
