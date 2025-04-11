from collections.abc import Mapping
from typing import Iterable, Optional, final, override

from flip.core.error import Error
from flip.core.tickable import Tickable
from flip.core.validatable import Validatable


class Component(Tickable, Validatable):
    class KeyError(Error, KeyError): ...

    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional["Component"] = None,
        children: Optional[Iterable["Component"]] = None,
        pins: Optional[Iterable["pin.Pin"]] = None,
    ) -> None:
        Tickable.__init__(self)
        Validatable.__init__(self)
        self.__name = name or self.__class__.__name__
        self.__parent: Optional[Component] = None
        self.__children = frozenset[Component]()
        self.__pins = frozenset[pin.Pin]()
        with self._pause_validation():
            if parent is not None:
                self.parent = parent
            if children is not None:
                self.children = frozenset(children)
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
        return self.name

    @property
    def name(self) -> str:
        return self.__name

    @final
    @property
    def parent(self) -> Optional["Component"]:
        return self.__parent

    @final
    @parent.setter
    def parent(self, parent: Optional["Component"]) -> None:
        if parent is not self.__parent:
            with self._pause_validation():
                if self.__parent is not None:
                    self.__parent.children -= frozenset({self})
                self.__parent = parent
                if self.__parent is not None:
                    self.__parent.children |= frozenset({self})

    @final
    @property
    def children(self) -> frozenset["Component"]:
        return self.__children

    @final
    @children.setter
    def children(self, children: frozenset["Component"]) -> None:
        if children != self.__children:
            with self._pause_validation():
                new_children = children - self.__children
                removed_children = self.__children - children
                self.__children = children
                for child in new_children:
                    child.parent = self
                for child in removed_children:
                    child.parent = None

    @property
    def children_by_name(self) -> Mapping[str, "Component"]:
        return {child.name: child for child in self.children}

    def child(self, name: str) -> "Component":
        names = name.split(".")
        node = self
        for name in names:
            try:
                node = node.children_by_name[name]
            except KeyError as e:
                raise self._error(f"no child named {name}", self.KeyError) from e
        return node

    @property
    def path(self) -> str:
        if self.parent is not None:
            return self.parent.path + "." + self.name
        else:
            return self.name

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
                    pin.component = self
                for pin in removed_pins:
                    pin.component = None

    @property
    def pins_by_name(self) -> Mapping[str, "pin.Pin"]:
        return {pin.name: pin for pin in self.pins}

    def pin(self, name: str) -> "pin.Pin":
        node = self
        names = name.split(".")
        for name in names[:-1]:
            node = node.child(name)
        try:
            return node.pins_by_name[names[-1]]
        except KeyError as e:
            raise self._error(f"no pin named {name}", self.KeyError) from e

    @override
    def _validate(self) -> None:
        if self.parent is not None and self not in self.parent.children:
            raise self._validation_error(f"{self} not in parent {self.parent}")
        for child in self.children:
            if child.parent is not self:
                raise self._validation_error(f"child {child} not in parent {self}")
            child.validate()
        for pin_ in self.pins:
            if pin_.component is not self:
                raise self._validation_error(f"pin {pin_} not in component {self}")
            pin_.validate()

        def _find_duplicates(names: Iterable[str]) -> list[str]:
            seen = set[str]()
            duplicates = set[str]()
            for name in names:
                if name in seen:
                    duplicates.add(name)
                seen.add(name)
            return list(duplicates)

        child_duplicates = _find_duplicates(child.name for child in self.children)
        if child_duplicates:
            raise self._validation_error(
                f"duplicate children: {', '.join(child_duplicates)}"
            )
        pin_duplicates = _find_duplicates(pin_.name for pin_ in self.pins)
        if pin_duplicates:
            raise self._validation_error(f"duplicate pins: {', '.join(pin_duplicates)}")
        duplicates = _find_duplicates(
            [child.name for child in self.children] + [pin.name for pin in self.pins]
        )
        if duplicates:
            raise self._validation_error(
                f"duplicate pin + child names: {', '.join(duplicates)}"
            )

    @property
    @override
    def _tickable_children(self) -> Iterable[Tickable]:
        yield from self.children
        yield from self.pins


from flip.core import pin
