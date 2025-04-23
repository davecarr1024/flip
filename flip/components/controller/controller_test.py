import pytest

from flip.bytes import Byte
from flip.components import Bus, Component, Register, Status
from flip.components.controller import Controller, Instruction, InstructionSet, Step


def test_controller() -> None:
    # computer with a single instruction that copies the value of
    # register a to register x iff tax_enable is True
    root = Component()
    bus = Bus(name="bus", parent=root)
    Controller(
        instruction_set=InstructionSet.create(
            instructions={
                Instruction.create(
                    name="tax",
                    opcode=Byte(0x00),
                    statuses={"tax_enable": True},
                    steps=[
                        Step.create(
                            [
                                "a.write",
                                "x.read",
                                "controller.step_counter.reset",
                            ]
                        ),
                    ],
                ),
                Instruction.create(
                    name="tax",
                    opcode=Byte(0x00),
                    statuses={"tax_enable": False},
                    steps=[
                        Step.create(
                            [
                                "controller.step_counter.reset",
                            ]
                        ),
                    ],
                ),
            }
        ),
        parent=root,
        name="controller",
        bus=bus,
    )
    a = Register(
        name="a",
        parent=root,
        bus=bus,
    )
    x = Register(
        name="x",
        parent=root,
        bus=bus,
    )
    tax_enable = Status(
        name="tax_enable",
        parent=root,
    )

    # set initial state: a = 0x01, x = 0x00, tax_enable = False
    a.value = Byte(0x01)
    assert a.value == Byte(0x01)
    assert x.value == Byte(0x00)
    assert tax_enable.value is False

    # tick the controller: no change
    root.tick()
    assert a.value == Byte(0x01)
    assert x.value == Byte(0x00)

    # set tax_enable to True: a = 0x01, x = 0x00, tax_enable = True
    tax_enable.value = True
    assert tax_enable.value is True
    assert a.value == Byte(0x01)
    assert x.value == Byte(0x00)

    # tick the controller: a = 0x01, x = 0x01
    root.tick()
    assert a.value == Byte(0x01)
    assert x.value == Byte(0x01)


def test_unknown_control() -> None:
    # same computer as above, but remove the registers so we
    # don't have any control to be setting with this isntruction
    root = Component()
    bus = Bus(name="bus", parent=root)
    Controller(
        instruction_set=InstructionSet.create(
            instructions={
                Instruction.create(
                    name="tax",
                    opcode=Byte(0x00),
                    steps=[
                        Step.create(
                            [
                                "a.write",
                                "x.read",
                                "controller.step_counter.reset",
                            ]
                        ),
                    ],
                ),
            }
        ),
        parent=root,
        name="controller",
        bus=bus,
    )
    with pytest.raises(Controller.KeyError):
        root.tick()
