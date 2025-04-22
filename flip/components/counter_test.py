from flip.components import Bus, Counter


def test_idle() -> None:
    bus = Bus(name="bus")
    counter = Counter(name="counter", bus=bus, parent=bus)
    assert counter.value == 0
    bus.tick()
    assert counter.value == 0


def test_increment() -> None:
    bus = Bus(name="bus")
    counter = Counter(name="counter", bus=bus, parent=bus)
    counter.enable_increment = True
    assert counter.value == 0
    bus.tick()
    assert counter.value == 1
    assert not counter.enable_increment


def test_reset() -> None:
    bus = Bus(name="bus")
    counter = Counter(name="counter", bus=bus, parent=bus)
    counter.enable_reset = True
    counter.value = 1
    assert counter.value == 1
    bus.tick()
    assert counter.value == 0
    assert not counter.enable_reset
