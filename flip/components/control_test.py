from flip.components import Component, Control


def test_ctor_name() -> None:
    c = Control(name="c")
    assert c.name == "c"


def test_ctor_parent() -> None:
    p = Component(name="p")
    c = Control(name="c", parent=p)
    assert c.parent is p
    assert p.children == {c}


def test_controls() -> None:
    p = Component(name="p")
    c = Control(name="c", parent=p)
    assert p.controls == {c}


def test_controls_by_path() -> None:
    p = Component(name="p")
    c = Control(name="c", parent=p)
    assert p.controls_by_path == {"c": c}


def test_set_value() -> None:
    c = Control(name="c")
    assert not c.value
    c.value = True
    assert c.value
    c.value = False
    assert not c.value


def test_aggregate_controls() -> None:
    g = Component(name="g")
    p1 = Component(name="p1", parent=g)
    p2 = Component(name="p2", parent=g)
    c1 = Control(name="c1", parent=p1)
    c2 = Control(name="c2", parent=p2)
    assert g.controls == {c1, c2}
    assert p1.controls == {c1}
    assert p2.controls == {c2}
    assert g.controls_by_path == {"p1.c1": c1, "p2.c2": c2}


def test_clear_inactive() -> None:
    # c is a non-auto-clearing control, so clear control is created
    c = Control(name="c", auto_clear=False)

    # if value is true and clear is false, value should remain true
    c.value = True
    assert c.clear is not None and not c.clear
    c.tick()
    assert c.value


def test_clear_active() -> None:
    # c is a non-auto-clearing control, so clear control is created
    c = Control(name="c", auto_clear=False)

    # if value is true and clear is true, value should become false
    # and clear should auto-clear
    c.clear = True
    c.tick()
    assert not c.value
    assert c.clear is not None and not c.clear


def test_clear_not_present_when_auto_clear() -> None:
    assert Control(name="c", auto_clear=True).clear is None
