from typing import Iterable, final


class Tickable:
    @property
    def _tickable_children(self) -> Iterable["Tickable"]:
        return []

    def _tick_send(self) -> None: ...

    @final
    def tick_send(self) -> None:
        self._tick_send()
        for child in self._tickable_children:
            child.tick_send()

    def _tick_propagate(self) -> None: ...

    @final
    def tick_propagate(self) -> None:
        self._tick_propagate()
        for child in self._tickable_children:
            child.tick_propagate()

    def _tick_receive(self) -> None: ...

    @final
    def tick_receive(self) -> None:
        self._tick_receive()
        for child in self._tickable_children:
            child.tick_receive()

    def _tick_react(self) -> None: ...

    @final
    def tick_react(self) -> None:
        self._tick_react()
        for child in self._tickable_children:
            child.tick_react()
