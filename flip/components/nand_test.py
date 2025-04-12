from flip.components import Nand
from flip.core import Pin


def test_create() -> None:
    a = Pin("a")
    b = Pin("b")
    y = Nand.create(a, b, name="my_nand")
    c = y.component
    assert isinstance(c, Nand)
    assert c.name == "my_nand"
    assert a.is_connected_to(c.a)
    assert b.is_connected_to(c.b)
    assert y.is_connected_to(c.y)
