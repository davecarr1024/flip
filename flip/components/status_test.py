from flip.components import Component, Status


def test_ctor() -> None:
    p = Component(name="p")
    s = Status(name="s", parent=p)
    assert s.name == "s"
    assert s.parent is p
    assert p.children == {s}
    assert p.statuses == {s}
    assert p.statuses_by_path == {"s": s}
    assert s.statuses == {s}
    assert s.statuses_by_path == {"s": s}
    assert s.value is False


def test_set_value() -> None:
    p = Component(name="p")
    s = Status(name="s", parent=p)
    assert not s.value
    s.value = True
    assert s.value
    s.value = False
    assert not s.value
