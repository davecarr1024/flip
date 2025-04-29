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
        self.__clear: Optional[Control] = (
            Control(
                name="clear",
                parent=self,
                auto_clear=True,
            )
            if not self.__auto_clear
            else None
        )

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
    def clear(self) -> Optional[bool]:
        return self.__clear.value if self.__clear is not None else None

    @clear.setter
    def clear(self, value: bool) -> None:
        if self.__clear is not None:
            self.__clear.value = value

    @property
    @override
    def controls(self) -> frozenset["Control"]:
        return super().controls | frozenset({self})

    @override
    def _tick_clear(self) -> None:
        if self.__auto_clear:
            self.value = False

    @override
    def _tick_process(self) -> None:
        if self.__clear is not None and self.__clear.value:
            self.value = False
