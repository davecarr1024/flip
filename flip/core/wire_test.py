import pytest

from flip.core import Component, Pin, Simulation, Wire


def test_ctor_empty() -> None:
    w = Wire()
    assert w.pins == frozenset()


def test_ctor_pins() -> None:
    p = Pin("pin")
    w = Wire([p])
    assert w.pins == frozenset({p})
    assert p.wires == frozenset({w})


def test_add_pin() -> None:
    p = Pin("pin")
    w = Wire()
    assert w.pins == frozenset()
    assert p.wires == frozenset()
    w.pins = frozenset({p})
    assert w.pins == frozenset({p})
    assert p.wires == frozenset({w})


def test_remove_pin() -> None:
    p = Pin("pin")
    w = Wire([p])
    assert w.pins == frozenset({p})
    assert p.wires == frozenset({w})
    w.pins = frozenset()
    assert w.pins == frozenset()
    assert p.wires == frozenset()


def test_eq() -> None:
    w = Wire()
    assert w == w
    assert w != Wire()


def test_invalid_pins() -> None:
    p = Pin("pin")
    w = Wire([p])
    with (
        pytest.raises(Wire.ValidationError),
        w._pause_validation(),  # type:ignore
        p._pause_validation(),  # type:ignore
    ):
        p._Pin__wires = frozenset()  # type:ignore


@pytest.mark.repeat(10)
def test_propagate_to_pin() -> None:
    p = Pin("pin")
    w = Wire([p])
    c = Component("component", pins=[p])
    sim = Simulation([c])
    sim.run_for(10)
    assert not w.value
    assert not p.value
    assert not w.next_value
    w.send(True)
    assert not w.value
    assert w.next_value
    sim.run_for(1)
    assert not w.value
    assert not p.value
    sim.run_for(10)
    assert w.value
    assert p.value


def test_invalid_timeout() -> None:
    with pytest.raises(Wire.ValidationError):
        Wire(value_timeout=-1)


def test_multiple_roots() -> None:
    c1 = Component("c1")
    c2 = Component("c2")
    p1 = Pin("p1", c1)
    p2 = Pin("p2", c2)
    with pytest.raises(Wire.ValidationError):
        Wire([p1, p2])
