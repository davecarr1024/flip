from typing import Iterable, Optional, override

from flip.core import Component, Pin, Simulation
from flip.core.tickable_test import TickCounter


class TickCounterComponent(Component, TickCounter):
    def __init__(
        self,
        /,
        max_ticks: Optional[int] = None,
        pins: Optional[Iterable[Pin]] = None,
    ) -> None:
        Component.__init__(self, pins=pins)
        TickCounter.__init__(self, max_ticks=max_ticks)


def test_run_for() -> None:
    tc = TickCounterComponent()
    sim = Simulation([tc])
    sim.run_for(10)
    assert tc.react_count == 10


def test_run_for_early_exit() -> None:
    tc = TickCounterComponent(max_ticks=10)
    sim = Simulation([tc])
    sim.run_for(100)
    assert tc.react_count == 10


def test_run_forever() -> None:
    tc = TickCounterComponent(max_ticks=10)
    sim = Simulation([tc])
    sim.run_forever()
    assert tc.react_count == 10


def test_run_until_stable() -> None:
    p = Pin("p")
    tc = TickCounterComponent(pins=[p])
    sim = Simulation([tc])
    sim.run_until_stable(stable_ticks=100)
    assert tc.react_count == 101


class Oscillator(Component):
    def __init__(
        self,
        /,
        period: int = 1,
        max_oscillations: Optional[int] = None,
    ) -> None:
        super().__init__()
        self.period = period
        self.output = Pin("output", self)
        self.ticks = 0
        self.num_oscillations = 0
        self.max_oscillations = max_oscillations

    @override
    def _tick_react(self) -> None:
        self.ticks += 1
        if (self.ticks % self.period) == 0 and (
            self.max_oscillations is None
            or self.num_oscillations < self.max_oscillations
        ):
            self.output.value = not self.output.value
            self.num_oscillations += 1


def test_run_until_stable_oscillator() -> None:
    osc = Oscillator(period=50, max_oscillations=100)
    sim = Simulation([osc])
    sim.run_until_stable(stable_ticks=100)
    assert osc.num_oscillations == 100
    assert osc.ticks == 5101


def test_run_until_stable_early_exit() -> None:
    tc = TickCounterComponent(max_ticks=10)
    sim = Simulation([tc])
    sim.run_until_stable(stable_ticks=100)
    assert tc.react_count == 10
