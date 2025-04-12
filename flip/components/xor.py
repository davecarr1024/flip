from typing import Optional

from flip.core import Component, Pin


class Xor(Component):
    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional[Component] = None,
    ) -> None:
        super().__init__(name=name, parent=parent)
        self.a = Pin("a", self)
        self.b = Pin("b", self)
        self.y = Pin("y", self)

        # (a | b) & !(a & b)
        or_ = self.or_(self.a, self.b, name="a | b")
        and_ = self.and_(self.a, self.b, name="a & b")
        not_and = self.not_(and_, name="!(a & b)")
        xor = self.and_(or_, not_and, name="(a | b) & !(a & b)")

        self.y.connect_to(xor)

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
