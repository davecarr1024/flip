import pytest

from flip.bytes import Byte
from flip.components import Bus, Component, Status
from flip.components.controller import StatusRegister

format = StatusRegister.Format(
    {
        "tax_enable": 0,
    }
)
root = Component()
bus = Bus(
    name="bus",
    parent=root,
)
status = StatusRegister(
    name="status",
    parent=root,
    bus=bus,
    format=format,
)
tax_enable = Status(
    name="tax_enable",
    parent=root,
)


def test_decode() -> None:
    status.value = Byte(0x00)
    assert status.status_values == {"tax_enable": False}
    status.value = Byte(0x01)
    assert status.status_values == {"tax_enable": True}


def test_encode() -> None:
    status.status_values = {"tax_enable": False}
    assert status.value == Byte(0x00)
    status.status_values = {"tax_enable": True}
    assert status.value == Byte(0x01)


def test_latch() -> None:
    # set initial state: tax_enable = False
    status.status_values = {"tax_enable": False}
    assert status.value == Byte(0x00)

    # enable tax_enable and latch
    tax_enable.value = True
    assert tax_enable.value is True
    status.latch = True
    assert status.latch
    root.tick()

    # verify that status was latched
    assert status.value == Byte(0x01)
    assert status.status_values == {"tax_enable": True}


def test_no_latch() -> None:
    # set initial state: tax_enable = False
    status.status_values = {"tax_enable": False}
    assert status.value == Byte(0x00)
    assert status.status_values == {"tax_enable": False}

    # enable tax_enable but don't latch
    tax_enable.value = True
    assert tax_enable.value is True
    root.tick()

    # verify that status was not latched
    assert status.value == Byte(0x00)
    assert status.status_values == {"tax_enable": False}


def test_invalid_format() -> None:
    with pytest.raises(StatusRegister.Format.Error):
        StatusRegister.Format({"tax_enable": 8})


def test_duplicate_format_entry() -> None:
    with pytest.raises(StatusRegister.Format.Error):
        StatusRegister.Format({"tax_enable": 0, "tax_disable": 0})


def test_encode_status_not_found() -> None:
    with pytest.raises(StatusRegister.Format.Error):
        StatusRegister.Format({"tax_enable": 0}).encode({"tax_disable": True})


def test_format_ctor() -> None:
    f = StatusRegister.Format({"tax_enable": 0, "tay_enable": 1})
    assert len(f) == 2
    assert dict(f) == {"tax_enable": 0, "tay_enable": 1}


def test_format_getitem_not_found() -> None:
    with pytest.raises(StatusRegister.Format.KeyError):
        StatusRegister.Format({"tax_enable": 0})["tay_enable"]


def test_root_status_not_found() -> None:
    root = Component()
    bus = Bus(
        name="bus",
        parent=root,
    )
    status = StatusRegister(
        name="status",
        parent=root,
        bus=bus,
        format=StatusRegister.Format({"tax_enable": 0}),
    )
    status.latch = True
    with pytest.raises(StatusRegister.Error):
        root.tick()
