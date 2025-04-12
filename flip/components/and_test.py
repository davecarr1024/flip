from pytest_subtests import SubTests

from flip.components import And
from flip.core import Component, Pin, Simulation


def test_create() -> None:
    a = Pin("a")
    b = Pin("b")
    c = Component("c", pins=[a, b])
    y = c.and_(a, b, name="my_and")
    assert y.root is c
    assert isinstance(y.component, And)
    assert y.component.name == "my_and"
    assert y.path == "c.my_and.y"


def test_and(subtests: SubTests) -> None:
    for a_value, b_value, y_value in list[tuple[bool, bool, bool]](
        [
            (False, False, False),
            (False, True, False),
            (True, False, False),
            (True, True, True),
        ]
    ):
        with subtests.test(a=a_value, b=b_value, y=y_value):
            a = Pin("a")
            b = Pin("b")
            c = Component("c", pins=[a, b])
            y = c.and_(a, b)
            sim = Simulation([c])
            sim.run_until_stable()
            a.value = a_value
            b.value = b_value
            sim.run_until_stable()
            assert y.value == y_value
