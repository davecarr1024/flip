from pytest_subtests import SubTests

from flip.components import Nand
from flip.core import Simulation


def test_react(subtests: SubTests) -> None:
    for a, b, y in list[
        tuple[
            bool,
            bool,
            bool,
        ]
    ](
        [
            (False, False, True),
            (False, True, True),
            (True, False, True),
            (True, True, False),
        ]
    ):
        with subtests.test(a=a, b=b, y=y):
            n = Nand()
            sim = Simulation([n])
            n.a = a
            n.b = b
            sim.run_for(1)
            assert n.y == y
