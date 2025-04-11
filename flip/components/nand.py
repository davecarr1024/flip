from typing import Optional, override

from flip.core import Component, Pin


class Nand(Component):
    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional[Component] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.a = Pin("a", self)
        self.b = Pin("b", self)
        self.y = Pin("y", self)
        self.pins = frozenset({self.a, self.b, self.y})

    @override
    def __str__(self) -> str:
        return f"Nand({self.a.value}, {self.b.value}) -> {self.y.value}"

    @override
    def _tick_react(self) -> None:
        self.y.value = not (self.a.value and self.b.value)
