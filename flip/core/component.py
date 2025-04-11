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
    ) -> None:
        Tickable.__init__(self)
        Validatable.__init__(self)
        self.__name = name or self.__class__.__name__
        self.__parent: Optional[Component] = None
        self.__children = frozenset[Component]()
        with self._pause_validation():
            if parent is not None:
                self.parent = parent
            if children is not None:
                for child in children:
                    self.add_child(child)

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
                    self.__parent.remove_child(self)
                self.__parent = parent
                if self.__parent is not None:
                    self.__parent.add_child(self)

    @final
    @property
    def children(self) -> frozenset["Component"]:
        return self.__children

    def add_child(self, child: "Component") -> None:
        if child not in self.children:
            with self._pause_validation():
                self.__children |= frozenset({child})
                child.parent = self

    def remove_child(self, child: "Component") -> None:
        if child in self.children:
            with self._pause_validation():
                self.__children -= frozenset({child})
                child.parent = None

    @property
    def children_by_name(self) -> Mapping[str, "Component"]:
        return {child.name: child for child in self.__children}

    def child(self, name: str) -> "Component":
        names = name.split(".")
        node = self
        for name in names:
            try:
                node = node.children_by_name[name]
            except KeyError as e:
                raise self._error(f"no child named {name}", self.KeyError) from e
        return node

    @override
    def _validate(self) -> None:
        if self.parent is not None and self not in self.parent.children:
            raise self._validation_error(f"{self} not in parent {self.parent}")
        for child in self.children:
            if child.parent is not self:
                raise self._validation_error(f"child {child} not in parent {self}")
            child._validate()

    @property
    @override
    def _tickable_children(self) -> Iterable[Tickable]:
        return self.children
