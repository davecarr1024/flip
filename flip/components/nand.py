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

    @override
    def _tick_react(self) -> None:
        self.y.value = not (self.a.value and self.b.value)

    @classmethod
    def create(
        cls,
        a: Pin,
        b: Pin,
        /,
        name: Optional[str] = None,
        parent: Optional[Component] = None,
    ) -> Pin:
        n = cls(name=name, parent=parent)
        a.connect_to(n.a)
        b.connect_to(n.b)
        return n.y
