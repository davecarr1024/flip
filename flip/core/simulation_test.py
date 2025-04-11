from typing import Optional, override

from flip.core.component import Component
from flip.core.simulation import Simulation


class TickCounter(Component):
    def __init__(
        self,
        max_ticks: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.ticks = 0
        self.max_ticks = max_ticks

    @override
    def tick(self) -> None:
        self.ticks += 1
        if self.max_ticks is not None and self.ticks >= self.max_ticks:
            raise Simulation.EndSimulation()


def test_run_for() -> None:
    tc = TickCounter()
    sim = Simulation([tc])
    sim.run_for(10)
    assert tc.ticks == 10


def test_run_forever() -> None:
    tc = TickCounter(10)
    sim = Simulation([tc])
    sim.run_forever()
    assert tc.ticks == 10
