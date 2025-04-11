from typing import Optional

from flip.core.component import Component
from flip.core.simulation import Simulation
from flip.core.tickable_test import TickCounter


class _TickCounter(Component, TickCounter):
    def __init__(
        self,
        /,
        max_ticks: Optional[int] = None,
    ) -> None:
        Component.__init__(self)
        TickCounter.__init__(self, max_ticks=max_ticks)


def test_run_for() -> None:
    tc = _TickCounter()
    sim = Simulation([tc])
    sim.run_for(10)
    assert tc.react_count == 10


def test_run_forever() -> None:
    tc = _TickCounter(max_ticks=10)
    sim = Simulation([tc])
    sim.run_forever()
    assert tc.react_count == 10
