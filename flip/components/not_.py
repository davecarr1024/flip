from typing import Optional

from flip.core import Component, Pin


class Not(Component):
    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional[Component] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.a = Pin("a", self)
        self.y = Pin("y", self)
        self.y.connect_to(self.nand(self.a, self.a))

    @classmethod
    def create(
        cls,
        a: Pin,
        /,
        name: Optional[str] = None,
        parent: Optional[Component] = None,
    ) -> Pin:
        not_ = cls(name=name, parent=parent)
        a.connect_to(not_.a)
        return not_.y
