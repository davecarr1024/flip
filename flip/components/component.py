from collections.abc import Mapping
from contextlib import contextmanager
from typing import Iterable, Iterator, Optional, Type, final, override

from flip.core import Error, Validatable


class Component(Validatable):
    class Error(Error): ...

    class KeyError(Error, KeyError): ...

    def __init__(
        self,
        name: Optional[str] = None,
        parent: Optional["Component"] = None,
        children: Optional[Iterable["Component"]] = None,
    ) -> None:
        super().__init__()
        self.__name = name or self.__class__.__name__
        self.__parent: Optional[Component] = None
        self.__children: frozenset[Component] = frozenset()
        self.__enable_logging: bool = False

        self.__path: Optional[str] = None
        self.__children_by_name: Optional[Mapping[str, Component]] = None
        self.__controls: Optional[frozenset["control.Control"]] = None
        self.__controls_by_path: Optional[Mapping[str, "control.Control"]] = None
        self.__statuses: Optional[frozenset["status.Status"]] = None
        self.__statuses_by_path: Optional[Mapping[str, "status.Status"]] = None

        with self._pause_validation():
            if parent is not None:
                self.parent = parent
            if children is not None:
                self.children = children

    def _invalidate_cache(
        self,
        traversed: Optional[frozenset["Component"]] = None,
    ) -> None:
        if traversed is not None and self in traversed:
            return
        traversed_ = (traversed or frozenset()) | (frozenset({self}))
        self.__path = None
        self.__children_by_name = None
        self.__controls = None
        self.__controls_by_path = None
        self.__statuses = None
        self.__statuses_by_path = None
        if self.parent is not None:
            self.parent._invalidate_cache(traversed_)
        for child in self.children:
            child._invalidate_cache(traversed_)

    @override
    def __eq__(self, other: object) -> bool:
        return self is other

    @override
    def __hash__(self) -> int:
        return id(self)

    @override
    def __repr__(self) -> str:
        return self.path

    @override
    @final
    def __str__(self) -> str:
        return self._str(0)

    def _str(self, tabs: int) -> str:
        s = "  " * tabs + self._str_line()
        for child in self.children:
            s += "\n" + child._str(tabs + 1)
        return s

    def _str_line(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"

    @property
    def name(self) -> str:
        return self.__name

    @property
    def root(self) -> "Component":
        if parent := self.parent:
            return parent.root
        return self

    @property
    def path(self) -> str:
        if self.__path is None:
            if self.parent is None:
                self.__path = ""
            elif self.parent.path == "":
                self.__path = self.name
            else:
                self.__path = f"{self.parent.path}.{self.name}"
        return self.__path

    @property
    def parent(self) -> Optional["Component"]:
        return self.__parent

    @parent.setter
    def parent(self, parent: Optional["Component"]) -> None:
        if parent != self.__parent:
            with self._pause_validation():
                self._invalidate_cache()
                if self.__parent is not None:
                    self.__parent.remove_child(self)
                self.__parent = parent
                if self.__parent is not None:
                    self.__parent.add_child(self)

    @property
    def children(self) -> frozenset["Component"]:
        return self.__children

    @children.setter
    def children(self, children: Iterable["Component"]) -> None:
        children_ = frozenset(children)
        if children_ != self.__children:
            with self._pause_validation():
                self._invalidate_cache()
                added_children = children_ - self.__children
                removed_children = self.__children - children_
                self.__children = children_
                for child in added_children:
                    child.parent = self
                for child in removed_children:
                    child.parent = None

    def add_child(self, child: "Component") -> None:
        self.children |= {child}

    def remove_child(self, child: "Component") -> None:
        self.children -= {child}

    @property
    def children_by_name(self) -> Mapping[str, "Component"]:
        if self.__children_by_name is None:
            self.__children_by_name = {child.name: child for child in self.children}
        return self.__children_by_name

    def child(self, name: str) -> "Component":
        if (dot_pos := name.find(".")) != -1:
            return self.child(name[:dot_pos]).child(name[dot_pos + 1 :])
        try:
            return self.children_by_name[name]
        except KeyError as e:
            raise self._error(f"Child {name} not found.", self.KeyError) from e

    @override
    def _validate(self) -> None:
        if self.__parent is not None and self not in self.__parent.__children:
            raise self._validation_error(
                f"Parent {self.__parent} does not contain child {self}."
            )
        if len(self.__children) != len({child.name for child in self.__children}):
            raise self._validation_error("duplicate child names.")
        for child in self.__children:
            if child.__parent is not self:
                raise self._validation_error(
                    f"Child {child} does not have parent {self}."
                )
            child.validate()

    @property
    def controls(self) -> frozenset["control.Control"]:
        if self.__controls is None:
            self.__controls = frozenset[control.Control]().union(
                *[child.controls for child in self.children]
            )
        return self.__controls

    @property
    def controls_by_path(self) -> Mapping[str, "control.Control"]:
        if self.__controls_by_path is None:
            self.__controls_by_path = {
                control.path: control for control in self.controls
            }
        return self.__controls_by_path

    @property
    def statuses(self) -> frozenset["status.Status"]:
        if self.__statuses is None:
            self.__statuses = frozenset[status.Status]().union(
                *[child.statuses for child in self.children]
            )
        return self.__statuses

    @property
    def statuses_by_path(self) -> Mapping[str, "status.Status"]:
        if self.__statuses_by_path is None:
            self.__statuses_by_path = {status.path: status for status in self.statuses}
        return self.__statuses_by_path

    @final
    def tick_control(self) -> None:
        with self._log_context("tick_control"):
            self._tick_control()
            for child in self.children:
                child.tick_control()

    def _tick_control(self) -> None: ...

    @final
    def tick_write(self) -> None:
        with self._log_context("tick_write"):
            self._tick_write()
            for child in self.children:
                child.tick_write()

    def _tick_write(self) -> None: ...

    @final
    def tick_read(self) -> None:
        with self._log_context("tick_read"):
            self._tick_read()
            for child in self.children:
                child.tick_read()

    def _tick_read(self) -> None: ...

    @final
    def tick_process(self) -> None:
        with self._log_context("tick_process"):
            self._tick_process()
            for child in self.children:
                child.tick_process()

    def _tick_process(self) -> None: ...

    @final
    def tick_clear(self) -> None:
        with self._log_context("tick_clear"):
            self._tick_clear()
            for child in self.children:
                child.tick_clear()

    def _tick_clear(self) -> None: ...

    def __tick(self) -> None:
        with self._log_context("tick"):
            self.tick_control()
            self.tick_write()
            self.tick_read()
            self.tick_process()
            self.tick_clear()

    @final
    def tick(self) -> None:
        self.root.__tick()

    __log_context = list[str]()

    @property
    def enable_logging(self) -> bool:
        return self.__enable_logging

    @enable_logging.setter
    def enable_logging(self, enable_logging: bool) -> None:
        self.__enable_logging = enable_logging
        if self.parent is not None:
            self.parent.enable_logging = enable_logging

    @final
    @contextmanager
    def _log_context(self, message: str) -> Iterator[None]:
        path = self.path
        try:
            if path != "":
                self.__log_context.append(f"{path}.{message}")
            yield
        finally:
            if path != "":
                self.__log_context.pop()

    @final
    def _log(self, message: str) -> None:
        if not self.enable_logging:
            return
        for tabs, context in enumerate(self.__log_context):
            print(f'{"  " * tabs}{context}')
        print(f'{"  "*len(self.__log_context)}{message}')

    @override
    def _error[E: Error](self, message: str, type: Type[E] = Error) -> E:
        return super()._error(message=f"{self.path}: {message}", type=type)


from flip.components import control, status
