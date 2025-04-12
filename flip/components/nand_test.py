from pytest_subtests import SubTests

from flip.components import Nand
from flip.core import Component, Pin, Simulation


def test_create() -> None:
    a = Pin("a")
    b = Pin("b")
    c = Component("c", pins=[a, b])
    y = Nand.create(a, b, name="my_nand", parent=c)
    nand = y.component
    assert isinstance(nand, Nand)
    assert nand.parent is c
    assert nand.name == "my_nand"
    assert a.is_connected_to(nand.a)
    assert b.is_connected_to(nand.b)
    assert y.is_connected_to(nand.y)


def test_nand(subtests: SubTests) -> None:
    for a, b, y in list[tuple[bool, bool, bool]](
        [
            (False, False, True),
            (False, True, True),
            (True, False, True),
            (True, True, False),
        ]
    ):
        with subtests.test(a=a, b=b, y=y):
            a_pin = Pin("a")
            b_pin = Pin("b")
            c = Component("c", pins=[a_pin, b_pin])
            y_pin = Nand.create(a_pin, b_pin, parent=c)
            sim = Simulation([c])
            print(f"a_pin.value = {a_pin.value}")
            print(f"b_pin.value = {b_pin.value}")
            print(f"y_pin.value = {y_pin.value}")
            nand = y_pin.component
            assert isinstance(nand, Nand)
            assert nand.parent is c
            assert nand.root is sim
            assert set(nand.a.connected_pins()) == {a_pin, nand.a}
            assert set(nand.b.connected_pins()) == {b_pin, nand.b}
            assert set(nand.y.connected_pins()) == {y_pin, nand.y}
            print("setting a and b...")
            a_pin.value = a
            b_pin.value = b
            print("running simulation...")
            sim.run_until_stable()
            print(f"a_pin.value = {a_pin.value}")
            print(f"b_pin.value = {b_pin.value}")
            print(f"y_pin.value = {y_pin.value}")
            assert nand.a.value == a
            assert nand.b.value == b
            assert y_pin.value == y
