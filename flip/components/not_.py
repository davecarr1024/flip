from typing import Optional

from flip.components import Nand
from flip.core import Component, Pin


class Not(Component):
    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional[Component] = None,
        a_connect_to: Optional[Pin] = None,
        y_connect_to: Optional[Pin] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.__a = Pin("a", self, connect_to=a_connect_to)
        self.__y = Pin("y", self, connect_to=y_connect_to)
        self.__nand = Nand(
            parent=self,
            a_connect_to=self.__a,
            b_connect_to=self.__a,
            y_connect_to=self.__y,
        )
        self.pins = frozenset({self.__a, self.__y})

    @property
    def a(self) -> bool:
        return self.__a.value

    @a.setter
    def a(self, value: bool) -> None:
        self.__a.value = value

    @property
    def y(self) -> bool:
        return self.__y.value
