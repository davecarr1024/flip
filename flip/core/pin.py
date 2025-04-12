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
            self._mark_wires_pending()

    def _mark_wires_pending(self) -> None:
        # print(f"pin {self} marking wires pending {self.wires}")
        self.__pending_wires |= self.wires

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
    def __repr__(self) -> str:
        return self.path

    @property
    def component(self) -> Optional["component.Component"]:
        return self.__component

    @property
    def root(self) -> Optional["component.Component"]:
        return self.component.root if self.component is not None else None

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
        # print(f"pin {self} wires setter: {wires}")
        if wires == self.__wires:
            # print("no diff")
            return
        with self._pause_validation():
            new_wires = wires - self.__wires
            removed_wires = self.__wires - wires
            self.__wires = wires
            # if new_wires:
            # print(f"new wires: {new_wires}")
            for wire in new_wires:
                wire.pins |= frozenset({self})
            # if removed_wires:
            # print(f"removed wires: {removed_wires}")
            for wire in removed_wires:
                wire.pins -= frozenset({self})
            self._mark_wires_pending()

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
        # print(f"pin {self} value getter: {self.__value}")
        return self.__value

    @value.setter
    def value(self, value: bool) -> None:
        # print(f"pin {self} value setter: {value}")
        if value != self.__value:
            # print(f"pin {self} value changed to {value}")
            self.__value = value
            self._mark_wires_pending()

    @override
    def _tick_send(self) -> None:
        # print(f"pin {self} _tick_send: pending_wires = {self.__pending_wires}")
        for wire_ in self.__pending_wires:
            # print(f"pin {self} sending value {self.value} to wire {wire_}")
            wire_.send(self.value)
        self.__pending_wires.clear()

    def connect_to(self, pin: "Pin") -> "wire.Wire":
        w = wire.Wire([self, pin])
        self._mark_wires_pending()
        return w

    def connected_pins(self) -> Iterable["Pin"]:
        seen = set[Pin]()
        pending = {self}
        while pending:
            pin = pending.pop()
            if pin not in seen:
                seen.add(pin)
                yield pin
                pending |= {p for w in pin.wires for p in w.pins if p not in seen}

    def is_connected_to(self, pin: "Pin") -> bool:
        return pin in self.connected_pins()


from flip.core import component, wire
