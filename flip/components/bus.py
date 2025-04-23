from typing import Iterable, Optional, override

from flip.bytes import Byte
from flip.components import component


class Bus(component.Component):
    class Error(component.Component.Error): ...

    class ConflictError(Error, ValueError): ...

    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional[component.Component] = None,
        children: Optional[Iterable[component.Component]] = None,
    ) -> None:
        super().__init__(name=name, parent=parent, children=children)
        self.__value: Optional[Byte] = None
        self.__setter: Optional[str] = None

    @override
    def _str_line(self) -> str:
        return f"Bus(name={self.name}, value={self.value}, setter={self.setter})"

    @property
    def value(self) -> Optional[Byte]:
        return self.__value

    @property
    def setter(self) -> Optional[str]:
        return self.__setter

    def set(self, value: Byte, setter: str | component.Component) -> None:
        if isinstance(setter, component.Component):
            setter = setter.path
        if self.__setter is not None and setter != self.__setter:
            raise self._error(
                f"Bus {self.path} is already set by {self.__setter}.",
                self.ConflictError,
            )
        self.__value = value
        self.__setter = setter

    @override
    def _tick_clear(self) -> None:
        self.__value = None
        self.__setter = None
