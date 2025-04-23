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
