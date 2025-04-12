from typing import Optional

from flip.core import Component, Pin


class Or(Component):
    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional[Component] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.a = Pin("a", self)
        self.b = Pin("b", self)
        self.y = Pin("y", self)
        self.y.connect_to(
            self.not_(
                self.and_(
                    self.not_(self.a, name="!a"),
                    self.not_(self.b, name="!b"),
                    name="!a & !b",
                ),
                name="!(!a & !b)",
            ),
        )

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
