from typing import Iterable, Optional

from flip.component import Component
from flip.error import Error


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

    def run_for(self, ticks: int) -> None:
        for _ in range(ticks):
            self.tick()

    def run_forever(self) -> None:
        try:
            while True:
                self.tick()
        except self.EndSimulation:
            pass
