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
        self.y = self.nand(self.a, self.a)
