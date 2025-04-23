from flip.bytes import Byte
from flip.components import Bus, Counter


def test_idle() -> None:
    bus = Bus(name="bus")
    counter = Counter(name="counter", bus=bus, parent=bus)
    assert counter.value == Byte(0)
    bus.tick()
    assert counter.value == Byte(0)


def test_increment() -> None:
    bus = Bus(name="bus")
    counter = Counter(name="counter", bus=bus, parent=bus)
    counter.increment = True
    assert counter.value == Byte(0)
    bus.tick()
    assert counter.value == Byte(1)
    assert not counter.increment


def test_reset() -> None:
    bus = Bus(name="bus")
    counter = Counter(name="counter", bus=bus, parent=bus)
    counter.reset = True
    counter.value = Byte(1)
    assert counter.value == Byte(1)
    bus.tick()
    assert counter.value == Byte(0)
    assert not counter.reset
