from pytest_subtests import SubTests

from flip.components import Not
from flip.core import Component, Pin, Simulation


def test_create(subtests: SubTests) -> None:
    a = Pin("a")
    c = Component("c", pins=[a])
    y = Not.create(a, parent=c)
    not_ = y.component
    assert isinstance(not_, Not)
    assert not_.parent is c
    assert a.is_connected_to(not_.a)
    assert y.is_connected_to(not_.y)


def test_not(subtests: SubTests) -> None:
    for a, y in list[tuple[bool, bool]](
        [
            (False, True),
            (True, False),
        ]
    ):
        with subtests.test(a=a, y=y):
            n = Not()
            sim = Simulation([n])
            n.a.value = a
            assert n.a.value == a
            sim.run_until_stable()
            assert n.y.value == y
