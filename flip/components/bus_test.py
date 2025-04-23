import pytest

from flip.bytes import Byte
from flip.components import Bus, Component


def test_set_value() -> None:
    bus = Bus()
    bus.set(Byte(1), "setter")
    assert bus.value == Byte(1)
    assert bus.setter == "setter"
    bus.tick_clear()
    assert bus.value is None
    assert bus.setter is None


def test_set_value_component() -> None:
    p = Component(name="p")
    c = Component(name="c", parent=p)
    bus = Bus()
    bus.set(Byte(1), c)
    assert bus.value == Byte(1)
    assert bus.setter == "c"
    bus.tick_clear()
    assert bus.value is None
    assert bus.setter is None


def test_set_value_conflict() -> None:
    bus = Bus()
    bus.set(Byte(1), "setter1")
    with pytest.raises(Bus.ConflictError):
        bus.set(Byte(2), "setter2")
