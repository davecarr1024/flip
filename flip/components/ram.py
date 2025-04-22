from collections.abc import MutableMapping
from typing import Iterator, Optional, override

from flip.bytes import Byte, Word
from flip.components import component


class Ram(component.Component, MutableMapping[Word, Byte]):
    class KeyError(component.Component.KeyError, KeyError): ...

    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional[component.Component] = None,
        data: Optional[MutableMapping[Word, Byte]] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.__data: MutableMapping[Word, Byte] = dict(data) if data is not None else {}

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

    @override
    def __iter__(self) -> Iterator[Word]:
        yield from self.__data

    @override
    def __len__(self) -> int:
        return len(self.__data)

    @override
    def _str_line(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, size={len(self)})"
