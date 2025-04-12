from typing import Iterable, Optional

from flip.core.component import Component, Snapshot
from flip.core.error import Error


class Simulation(Component):
    class EndSimulation(Error):
        def __init__(self, message: str = "end of simulation") -> None:
            super().__init__(message)

    def __init__(
        self,
        children: Optional[Iterable[Component]] = None,
        /,
        name: Optional[str] = None,
    ) -> None:
        super().__init__(name=name, children=children)

    def _tick(self) -> None:
        self.tick_send()
        self.tick_propagate()
        self.tick_receive()
        self.tick_react()

    def run_for(self, ticks: int) -> None:
        try:
            for _ in range(ticks):
                self._tick()
        except self.EndSimulation:
            pass

    def run_forever(self) -> None:
        try:
            while True:
                self._tick()
        except self.EndSimulation:
            pass

    def run_until_stable(self, stable_ticks: int = 100) -> None:
        try:
            last_snapshot: Optional[Snapshot] = None
            unchanged_ticks = 0
            while unchanged_ticks < stable_ticks:
                snapshot = self.snapshot()
                if snapshot == last_snapshot:
                    unchanged_ticks += 1
                else:
                    unchanged_ticks = 0
                last_snapshot = snapshot
                self._tick()
        except self.EndSimulation:
            pass
