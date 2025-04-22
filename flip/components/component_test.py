from typing import override

import pytest

from flip.components import Component


def test_ctor_name() -> None:
    c = Component(name="c")
    assert c.name == "c"


def test_eq() -> None:
    c = Component(name="c")
    assert c == c
    assert c != Component(name="c")
    assert hash(c) == hash(c)
    assert hash(c) != hash(Component(name="c"))


def test_ctor_parent() -> None:
    p = Component(name="p")
    c = Component(name="c", parent=p)
    assert c.parent is p
    assert p.children == {c}


def test_ctor_childeren() -> None:
    c = Component(name="c")
    p = Component(name="p", children=[c])
    assert c.parent is p
    assert p.children == {c}


def test_str() -> None:
    c = Component(name="c")
    p = Component(name="p", children=[c])
    assert str(p) == "Component(name=p)\n  Component(name=c)"


def test_root() -> None:
    g = Component(name="g")
    p = Component(name="p", parent=g)
    c = Component(name="c", parent=p)
    assert c.root is g
    assert p.root is g
    assert g.root is g


def test_path() -> None:
    g = Component(name="g")
    p = Component(name="p", parent=g)
    c = Component(name="c", parent=p)
    assert c.path == "g.p.c"
    assert p.path == "g.p"
    assert g.path == "g"


def test_children_by_name() -> None:
    c1 = Component(name="c1")
    c2 = Component(name="c2")
    p = Component(name="p", children=[c1, c2])
    assert p.children_by_name == {"c1": c1, "c2": c2}


def test_child() -> None:
    g = Component(name="g")
    p = Component(name="p", parent=g)
    c = Component(name="c", parent=p)
    assert g.child("p") is p
    assert g.child("p.c") is c
    assert p.child("c") is c
    with pytest.raises(Component.KeyError):
        g.child("x")


def test_set_parent() -> None:
    c = Component(name="c")
    p = Component(name="p")
    assert c.parent is None
    assert p.children == set()
    c.parent = p
    assert c.parent is p
    assert p.children == {c}
    c.parent = None
    assert c.parent is None
    assert p.children == set()


def test_set_children() -> None:
    c = Component(name="c")
    p = Component(name="p")
    assert c.parent is None
    assert p.children == set()
    p.children = {c}
    assert c.parent is p
    assert p.children == {c}
    p.children = set()
    assert c.parent is None
    assert p.children == set()


def test_add_child() -> None:
    c = Component(name="c")
    p = Component(name="p")
    assert c.parent is None
    assert p.children == set()
    p.add_child(c)
    assert c.parent is p
    assert p.children == {c}


def test_remove_child() -> None:
    p = Component(name="p")
    c = Component(name="c", parent=p)
    assert c.parent is p
    assert p.children == {c}
    p.remove_child(c)
    assert c.parent is None
    assert p.children == set()


def test_invalid_parent() -> None:
    p = Component(name="p")
    c = Component(name="c", parent=p)
    with (
        pytest.raises(Component.ValidationError),
        c._pause_validation(),  # type: ignore
        p._pause_validation(),  # type: ignore
    ):
        c._Component__parent = None  # type: ignore


def test_invalid_children() -> None:
    p = Component(name="p")
    c = Component(name="c", parent=p)
    with (
        pytest.raises(Component.ValidationError),
        c._pause_validation(),  # type: ignore
        p._pause_validation(),  # type: ignore
    ):
        p._Component__children = {}  # type: ignore


def test_tick() -> None:
    class Tickable(Component):
        def __init__(self) -> None:
            super().__init__()
            self.tick_control_called = False
            self.tick_write_called = False
            self.tick_read_called = False
            self.tick_clear_called = False

        @override
        def tick_control(self) -> None:
            self.tick_control_called = True

        @override
        def tick_write(self) -> None:
            self.tick_write_called = True

        @override
        def tick_read(self) -> None:
            self.tick_read_called = True

        @override
        def tick_clear(self) -> None:
            self.tick_clear_called = True

    t = Tickable()
    p = Component(name="p", children=[t])
    assert not t.tick_control_called
    assert not t.tick_write_called
    assert not t.tick_read_called
    assert not t.tick_clear_called
    p.tick()
    assert t.tick_control_called
    assert t.tick_write_called
    assert t.tick_read_called
    assert t.tick_clear_called
