import pytest

from flip.core import Component, Pin


def test_name() -> None:
    p = Pin("test")
    assert p.name == "test"


def test_eq() -> None:
    p = Pin("test")
    assert p == p
    assert p != Pin("test")


def test_ctor_component() -> None:
    c = Component("component")
    p = Pin("pin", c)
    assert p.component is c
    assert c.pins == frozenset({p})


def test_add_pin() -> None:
    c = Component("component")
    p = Pin("pin")
    assert p.component is None
    assert c.pins == frozenset()
    c.pins |= frozenset({p})
    assert p.component is c
    assert c.pins == frozenset({p})


def test_remove_pin() -> None:
    c = Component("component")
    p = Pin("pin", c)
    assert p.component is c
    assert c.pins == frozenset({p})
    c.pins -= frozenset({p})
    assert p.component is None
    assert c.pins == frozenset()


def test_invalid_component() -> None:
    p = Pin("pin")
    c = Component("component", pins=[p])
    with (
        pytest.raises(Component.ValidationError),
        c._pause_validation(),  # type:ignore
        p._pause_validation(),  # type:ignore
    ):
        c._Component__pins = frozenset()  # type:ignore
