from typing import Iterable, Optional, override

from flip.core import Simulation, Tickable


class TickCounter(Tickable):
    def __init__(
        self,
        children: Optional[Iterable[Tickable]] = None,
        /,
        max_ticks: Optional[int] = None,
    ) -> None:
        self.__tickable_children = list(children) if children else []
        self.send_count = 0
        self.propagate_count = 0
        self.receive_count = 0
        self.react_count = 0
        self.max_ticks = max_ticks

    @property
    @override
    def _tickable_children(self) -> Iterable[Tickable]:
        return self.__tickable_children

    @override
    def _tick_send(self) -> None:
        self.send_count += 1

    @override
    def _tick_propagate(self) -> None:
        self.propagate_count += 1

    @override
    def _tick_receive(self) -> None:
        self.receive_count += 1

    @override
    def _tick_react(self) -> None:
        self.react_count += 1
        if self.max_ticks is not None and self.react_count >= self.max_ticks:
            raise Simulation.EndSimulation()


def test_receive() -> None:
    c = TickCounter()
    p = TickCounter([c])
    p.tick_receive()
    assert c.receive_count == 1
    assert p.receive_count == 1


def test_defaults() -> None:
    t = Tickable()
    t.tick_send()
    t.tick_propagate()
    t.tick_receive()
    t.tick_react()
