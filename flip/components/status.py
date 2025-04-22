from typing import Optional, override

from flip.components import component


class Status(component.Component):
    def __init__(
        self,
        name: str,
        parent: Optional[component.Component] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.__value = False

    @property
    def value(self) -> bool:
        return self.__value

    @value.setter
    def value(self, value: bool) -> None:
        self.__value = value

    @property
    @override
    def statuses(self) -> frozenset["Status"]:
        return super().statuses | frozenset({self})
