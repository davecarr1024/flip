from typing import Iterable, Optional, override

from flip.core.tickable import Tickable
from flip.core.validatable import Validatable


class Pin(Tickable, Validatable):
    def __init__(
        self,
        name: str,
        component: Optional["component.Component"] = None,
        wires: Optional[Iterable["wire.Wire"]] = None,
        value: bool = False,
        connect_to: Optional["Pin"] = None,
    ) -> None:
        Tickable.__init__(self)
        Validatable.__init__(self)
        self.__name = name
        self.__component: Optional["component.Component"] = None
        self.__wires = frozenset[wire.Wire]()
        self.__value = value
        self.__pending_wires = set[wire.Wire]()
        with self._pause_validation():
            if component is not None:
                self.component = component
            if wires is not None:
                self.wires = frozenset(wires)
        if connect_to is not None:
            self.connect_to(connect_to)

    @property
    def name(self) -> str:
        return self.__name

    @property
    def path(self) -> str:
        if self.component is not None:
            return self.component.path + "." + self.name
        else:
            return self.name

    @override
    def __eq__(self, rhs: object) -> bool:
        return self is rhs

    @override
    def __hash__(self) -> int:
        return id(self)

    @override
    def __str__(self) -> str:
        return self.name

    @property
    def component(self) -> Optional["component.Component"]:
        return self.__component

    @component.setter
    def component(self, component: Optional["component.Component"]) -> None:
        if component is not self.__component:
            with self._pause_validation():
                if self.__component is not None:
                    self.__component.pins -= frozenset({self})
                self.__component = component
                if self.__component is not None:
                    self.__component.pins |= frozenset({self})

    @property
    def wires(self) -> frozenset["wire.Wire"]:
        return self.__wires

    @wires.setter
    def wires(self, wires: frozenset["wire.Wire"]) -> None:
        if wires != self.__wires:
            with self._pause_validation():
                new_wires = wires - self.__wires
                removed_wires = self.__wires - wires
                self.__wires = wires
                for wire in new_wires:
                    wire.pins |= frozenset({self})
                for wire in removed_wires:
                    wire.pins -= frozenset({self})

    @override
    def _validate(self) -> None:
        if self.component is not None and self not in self.component.pins:
            raise self._validation_error(f"{self} not in component {self.component}")
        for wire_ in self.wires:
            if self not in wire_.pins:
                raise self._validation_error(f"{self} not in wire {wire_}")

    @property
    @override
    def _tickable_children(self) -> Iterable[Tickable]:
        yield from self.wires

    @property
    def value(self) -> bool:
        return self.__value

    @value.setter
    def value(self, value: bool) -> None:
        if value != self.__value:
            print(f"pin {self} value changed to {value}")
            self.__value = value
            self.__pending_wires |= self.wires

    @override
    def _tick_send(self) -> None:
        for wire_ in self.__pending_wires:
            print(f"pin {self} sending value {self.value} to wire {wire_}")
            wire_.send(self.value)
        self.__pending_wires.clear()

    def connect_to(self, pin: "Pin") -> "wire.Wire":
        return wire.Wire([self, pin])


from flip.core import component, wire
