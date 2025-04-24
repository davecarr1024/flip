import pytest

from flip.bytes import Byte
from flip.components import Bus, Component, Register, Status
from flip.components.controller import Controller
from flip.instructions import (
    AddressingMode,
    Instruction,
    InstructionImpl,
    InstructionMode,
    InstructionSet,
    Step,
)


def test_controller() -> None:
    # computer with a single instruction that copies the value of
    # register a to register x iff tax_enable is True
    root = Component()
    bus = Bus(name="bus", parent=root)
    Controller(
        name="controller",
        parent=root,
        bus=bus,
        instruction_set=InstructionSet.create(
            instructions={
                Instruction.create(
                    name="tax",
                    modes={
                        InstructionMode.create(
                            mode=AddressingMode.NONE,
                            opcode=Byte(0x00),
                            impls={
                                InstructionImpl.create(
                                    steps=[
                                        Step.create(
                                            [
                                                "a.write",
                                                "x.read",
                                                "controller.step_counter.reset",
                                            ]
                                        ),
                                    ],
                                    statuses={"tax_enable": True},
                                ),
                                InstructionImpl.create(
                                    steps=[
                                        Step.create(
                                            [
                                                "controller.step_counter.reset",
                                            ]
                                        ),
                                    ],
                                    statuses={"tax_enable": False},
                                ),
                            },
                        ),
                    },
                )
            }
        ),
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


def test_unknown_signal() -> None:
    # same computer as above, but remove the tax_enable status so that
    # controller is trying to get a status that doesn't exist
    root = Component()
    bus = Bus(name="bus", parent=root)
    Controller(
        name="controller",
        parent=root,
        bus=bus,
        instruction_set=InstructionSet.create(
            instructions={
                Instruction.create(
                    name="tax",
                    modes={
                        InstructionMode.create(
                            mode=AddressingMode.NONE,
                            opcode=Byte(0x00),
                            impls={
                                InstructionImpl.create(
                                    steps=[
                                        Step.create(
                                            [
                                                "a.write",
                                                "x.read",
                                                "controller.step_counter.reset",
                                            ]
                                        ),
                                    ],
                                    statuses={"tax_enable": True},
                                ),
                                InstructionImpl.create(
                                    steps=[
                                        Step.create(
                                            [
                                                "controller.step_counter.reset",
                                            ]
                                        ),
                                    ],
                                    statuses={"tax_enable": False},
                                ),
                            },
                        ),
                    },
                )
            }
        ),
    )
    with pytest.raises(Controller.MissingStatusError):
        root.tick()


def test_unknown_control() -> None:
    # same computer as above, but remove the registers so we
    # don't have any control to be setting with this isntruction
    root = Component()
    bus = Bus(name="bus", parent=root)
    Controller(
        name="controller",
        parent=root,
        bus=bus,
        instruction_set=InstructionSet.create(
            instructions={
                Instruction.create_simple(
                    name="tax",
                    mode=AddressingMode.NONE,
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
                )
            },
        ),
    )
    with pytest.raises(Controller.MissingControlError):
        root.tick()
