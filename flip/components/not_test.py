from pytest_subtests import SubTests

from flip.components import Not
from flip.core import Simulation


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
