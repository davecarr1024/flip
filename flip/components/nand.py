from typing import Optional, override

from flip.core import Component, Pin


class Nand(Component):
    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional[Component] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.__a = Pin("a", self)
        self.__b = Pin("b", self)
        self.__y = Pin("y", self)
        self.pins = frozenset({self.__a, self.__b, self.__y})

    @override
    def __str__(self) -> str:
        return f"Nand({self.a}, {self.b}) -> {self.y}"

    @override
    def _tick_react(self) -> None:
        self._y = not (self.a and self.b)

    @property
    def a(self) -> bool:
        return self.__a.value

    @a.setter
    def a(self, value: bool) -> None:
        self.__a.value = value

    @property
    def b(self) -> bool:
        return self.__b.value

    @b.setter
    def b(self, value: bool) -> None:
        self.__b.value = value

    @property
    def _y(self) -> bool:
        return self.__y.value

    @_y.setter
    def _y(self, value: bool) -> None:
        self.__y.value = value

    @property
    def y(self) -> bool:
        return self._y
