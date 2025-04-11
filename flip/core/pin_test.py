import pytest

from flip.core import Component, Pin, Simulation, Wire


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


def test_ctor_wires() -> None:
    w = Wire()
    p = Pin("pin", wires=[w])
    assert p.wires == frozenset({w})
    assert w.pins == frozenset({p})


def test_add_wire() -> None:
    w = Wire()
    p = Pin("pin")
    assert p.wires == frozenset()
    assert w.pins == frozenset()
    p.wires |= frozenset({w})
    assert p.wires == frozenset({w})
    assert w.pins == frozenset({p})


def test_remove_wire() -> None:
    w = Wire()
    p = Pin("pin", wires=[w])
    assert p.wires == frozenset({w})
    assert w.pins == frozenset({p})
    p.wires -= frozenset({w})
    assert p.wires == frozenset()
    assert w.pins == frozenset()


def test_invalid_wires() -> None:
    p = Pin("pin")
    w = Wire(pins=[p])
    with (
        pytest.raises(Wire.ValidationError),
        w._pause_validation(),  # type:ignore
        p._pause_validation(),  # type:ignore
    ):
        w._Wire__pins = frozenset()  # type:ignore


@pytest.mark.repeat(10)
def test_propagate_to_pin() -> None:
    p1 = Pin("p1")
    p2 = Pin("p2")
    w = Wire([p1, p2])
    c = Component("c", pins=[p1, p2])
    sim = Simulation([c])
    assert not p1.value
    assert not p2.value
    assert not w.value
    p1.value = True
    sim.run_for(w.value_timeout)
    assert p1.value
    assert p2.value
    assert w.value


@pytest.mark.repeat(10)
def test_propagate_through_pin() -> None:
    p1 = Pin("p1")
    p2 = Pin("p2")
    p3 = Pin("p3")
    w1 = Wire([p1, p2])
    w2 = Wire([p2, p3])
    c1 = Component("c1", pins=[p1])
    c2 = Component("c2", pins=[p2])
    c3 = Component("c3", pins=[p3])
    sim = Simulation([c1, c2, c3])
    sim.run_for(100)
    assert not p1.value
    assert not p2.value
    assert not p3.value
    assert not w1.value
    assert not w2.value
    p1.value = True
    sim.run_for(w1.value_timeout + w2.value_timeout)
    assert p1.value
    assert w1.value
    assert p2.value
    assert w2.value
    assert p3.value
