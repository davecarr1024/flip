import pytest

from flip.core.component import Component


def test_ctor_empty() -> None:
    c = Component("test")
    assert c.name == "test"
    assert c.parent is None
    assert c.children == frozenset()


def test_ctor_parent() -> None:
    p = Component("parent")
    c = Component("child", parent=p)
    assert p.parent is None
    assert c.parent is p
    assert p.children == frozenset({c})
    assert c.children == frozenset()
    assert p.child("child") is c


def test_ctor_children() -> None:
    c = Component("child")
    p = Component("parent", children=[c])
    assert p.parent is None
    assert c.parent is p
    assert p.children == frozenset({c})
    assert c.children == frozenset()


def test_set_parent() -> None:
    p = Component("parent")
    c = Component("child")
    assert p.parent is None
    assert c.parent is None
    assert p.children == frozenset()
    assert c.children == frozenset()
    c.parent = p
    assert p.parent is None
    assert c.parent is p
    assert p.children == frozenset({c})
    assert c.children == frozenset()


def test_add_child() -> None:
    p = Component("parent")
    c = Component("child")
    assert p.parent is None
    assert c.parent is None
    assert p.children == frozenset()
    assert c.children == frozenset()
    p.add_child(c)
    assert p.parent is None
    assert c.parent is p
    assert p.children == frozenset({c})
    assert c.children == frozenset()


def test_remove_child() -> None:
    p = Component("parent")
    c = Component("child")
    p.add_child(c)
    assert p.parent is None
    assert c.parent is p
    assert p.children == frozenset({c})
    assert c.children == frozenset()
    p.remove_child(c)
    assert p.parent is None
    assert c.parent is None
    assert p.children == frozenset()
    assert c.children == frozenset()


def test_eq() -> None:
    assert Component("test") != Component("test")
    c = Component("test")
    assert c == c


def test_child_not_found() -> None:
    p = Component("parent")
    with pytest.raises(Component.KeyError):
        p.child("child")


def test_children_by_name() -> None:
    assert Component("test").children_by_name == {}
    p = Component("parent")
    c = Component("child", parent=p)
    assert p.children_by_name == {"child": c}


def test_get_child_by_name() -> None:
    p = Component("parent")
    c = Component("child", parent=p)
    assert p.child("child") is c


def test_get_grandchild_by_name() -> None:
    p = Component("parent")
    c = Component("child", parent=p)
    g = Component("grandchild", parent=c)
    assert p.child("child") is c
    assert p.child("child.grandchild") is g
    assert c.child("grandchild") is g


def test_default_name() -> None:
    class _Component(Component): ...

    assert _Component().name == "_Component"


def test_invalid_parent() -> None:
    p = Component("parent")
    c = Component("child", p)
    with (
        pytest.raises(Component.ValidationError),
        p._pause_validation(),  # type:ignore
        c._pause_validation(),  # type:ignore
    ):
        c._Component__parent = None  # type:ignore


def test_invalid_children() -> None:
    p = Component("parent")
    c = Component("child", p)
    with (
        pytest.raises(Component.ValidationError),
        p._pause_validation(),  # type:ignore
        c._pause_validation(),  # type:ignore
    ):
        p._Component__children = frozenset()  # type:ignore
