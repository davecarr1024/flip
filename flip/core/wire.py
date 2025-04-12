import random
from typing import Iterable, Optional, override

from flip.core.tickable import Tickable
from flip.core.validatable import Validatable


class Wire(Tickable, Validatable):
    MIN_VALUE_TIMEOUT = 5
    MAX_VALUE_TIMEOUT = 10

    def __init__(
        self,
        pins: Optional[Iterable["pin.Pin"]] = None,
        value: bool = False,
        value_timeout: Optional[int] = None,
    ) -> None:
        Tickable.__init__(self)
        Validatable.__init__(self)
        self.__pins = frozenset[pin.Pin]()
        self.__value = value
        self.__next_value = self.__value
        self.__value_timeout = value_timeout or random.randint(
            self.MIN_VALUE_TIMEOUT,
            self.MAX_VALUE_TIMEOUT,
        )
        if (
            self.__value_timeout < self.MIN_VALUE_TIMEOUT
            or self.__value_timeout > self.MAX_VALUE_TIMEOUT
        ):
            raise self._validation_error(
                f"value_timeout {self.__value_timeout} out of range "
                f"[{self.MIN_VALUE_TIMEOUT}, {self.MAX_VALUE_TIMEOUT}]"
            )
        self.__value_timer = 0
        self.__pending_pins = set[pin.Pin]()

        with self._pause_validation():
            if pins is not None:
                self.pins = frozenset(pins)

    @override
    def __eq__(self, rhs: object) -> bool:
        return self is rhs

    @override
    def __hash__(self) -> int:
        return id(self)

    @override
    def __str__(self) -> str:
        return f"Wire({', '.join(map(str, self.pins))})"

    @property
    def pins(self) -> frozenset["pin.Pin"]:
        return self.__pins

    @pins.setter
    def pins(self, pins: frozenset["pin.Pin"]) -> None:
        if pins != self.__pins:
            with self._pause_validation():
                new_pins = pins - self.__pins
                removed_pins = self.__pins - pins
                self.__pins = pins
                for pin in new_pins:
                    pin.wires |= frozenset({self})
                for pin in removed_pins:
                    pin.wires -= frozenset({self})

    @override
    def _validate(self) -> None:
        for pin_ in self.pins:
            if self not in pin_.wires:
                raise self._validation_error(f"pin {pin_} not in wire {self}")

    @property
    def next_value(self) -> bool:
        return self.__next_value

    @property
    def value_timeout(self) -> int:
        return self.__value_timeout

    @property
    def value(self) -> bool:
        return self.__value

    def send(self, value: bool) -> None:
        if value != self.__value:
            print(
                f"wire {self} received value {value} "
                f"and set timer to {self.__value_timeout}"
            )
            self.__next_value = value
            self.__value_timer = self.__value_timeout

    @override
    def _tick_propagate(self) -> None:
        if self.__next_value != self.__value and self.__value_timer > 0:
            self.__value_timer -= 1
            print(f"wire {self} timer is {self.__value_timer}")
            if self.__value_timer == 0:
                print(f"wire {self} value changed to {self.__next_value}")
                self.__value = self.__next_value
                self.__pending_pins |= self.pins

    @override
    def _tick_receive(self) -> None:
        for pin_ in self.__pending_pins:
            print(f"wire {self} sending value {self.__value} to pin {pin_}")
            pin_.value = self.__value
        self.__pending_pins.clear()


from flip.core import pin
