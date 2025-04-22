from typing import Iterable, Optional, override

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
        self.__value: Optional[int] = None
        self.__setter: Optional[str] = None

    @property
    def value(self) -> Optional[int]:
        return self.__value

    @property
    def setter(self) -> Optional[str]:
        return self.__setter

    def set(self, value: int, setter: str | component.Component) -> None:
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
    def tick_clear(self) -> None:
        super().tick_clear()
        self.__value = None
        self.__setter = None
