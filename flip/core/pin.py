from typing import Optional, override

from flip.core.tickable import Tickable
from flip.core.validatable import Validatable


class Pin(Tickable, Validatable):
    def __init__(
        self,
        name: str,
        component: Optional["component.Component"] = None,
    ) -> None:
        Tickable.__init__(self)
        Validatable.__init__(self)
        self.__name = name
        self.__component: Optional["component.Component"] = None
        with self._pause_validation():
            if component is not None:
                self.component = component

    @property
    def name(self) -> str:
        return self.__name

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

    @override
    def _validate(self) -> None:
        if self.component is not None and self not in self.component.pins:
            raise self._validation_error(f"{self} not in component {self.component}")


from flip.core import component
