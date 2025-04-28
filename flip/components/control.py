from typing import Optional, override

from flip.components import component


class Control(component.Component):
    def __init__(
        self,
        name: str,
        parent: Optional[component.Component] = None,
        auto_clear: bool = True,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.__value = False
        self.__auto_clear = auto_clear

    @override
    def _str_line(self) -> str:
        return f"Control(name={self.name}, value={self.value})"

    @property
    def value(self) -> bool:
        return self.__value

    @value.setter
    def value(self, value: bool) -> None:
        self.__value = value

    @property
    @override
    def controls(self) -> frozenset["Control"]:
        return frozenset({self})

    @override
    def _tick_clear(self) -> None:
        if self.__auto_clear:
            self.value = False
