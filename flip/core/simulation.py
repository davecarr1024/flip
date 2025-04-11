from typing import Iterable, Optional

from flip.core.component import Component
from flip.core.error import Error


class Simulation(Component):
    class EndSimulation(Error):
        def __init__(self, message: str = "end of simulation") -> None:
            super().__init__(message)

    def __init__(
        self,
        children: Iterable[Component],
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
        for _ in range(ticks):
            self._tick()

    def run_forever(self) -> None:
        try:
            while True:
                self._tick()
        except self.EndSimulation:
            pass
