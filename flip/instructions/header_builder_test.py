from flip.bytes import Byte
from flip.instructions import (
    AddressingMode,
    Instruction,
    InstructionImpl,
    InstructionMode,
    InstructionSet,
    Step,
)


def test_direct_step() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .step("c1")
        .header()
        .step("h1")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"h1"}),
                                    Step.create({"c1"}),
                                ],
                            ),
                        },
                    ),
                },
            ),
        },
    )


def test_step_control() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .step("c1")
        .header()
        .step()
        .control("h1")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"h1"}),
                                    Step.create({"c1"}),
                                ],
                            ),
                        },
                    ),
                },
            ),
        },
    )


def test_direct_step_during_step() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .step("c1")
        .header()
        .step()
        .control("h1")
        .step("h2")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"h1"}),
                                    Step.create({"h2"}),
                                    Step.create({"c1"}),
                                ],
                            ),
                        },
                    ),
                },
            ),
        }
    )


def test_step_control_during_step() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .step("c1")
        .header()
        .step()
        .control("h1")
        .step()
        .control("h2")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"h1"}),
                                    Step.create({"h2"}),
                                    Step.create({"c1"}),
                                ],
                            ),
                        },
                    ),
                },
            ),
        }
    )


def test_header_during_header() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .step("c1")
        .header()
        .header()
        .step("h1")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"h1"}),
                                    Step.create({"c1"}),
                                ],
                            ),
                        },
                    ),
                },
            ),
        }
    )


def test_header_during_header_step() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .step("c1")
        .header()
        .step()
        .control("h1")
        .header()
        .step("h2")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"h1"}),
                                    Step.create({"h2"}),
                                    Step.create({"c1"}),
                                ],
                            ),
                        },
                    ),
                },
            ),
        }
    )


def test_header_during_instruction() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .step("c1")
        .end_mode()
        .header()
        .step("h1")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"h1"}),
                                    Step.create({"c1"}),
                                ],
                            ),
                        },
                    ),
                },
            ),
        }
    )


def test_header_during_mode() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .step("c1")
        .end_impl()
        .header()
        .step("h1")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"h1"}),
                                    Step.create({"c1"}),
                                ],
                            ),
                        },
                    ),
                },
            )
        }
    )


def test_header_during_instruction_step() -> None:
    assert (
        InstructionSet.Builder()
        .instruction("i")
        .mode("absolute")
        .step()
        .control("c1")
        .header()
        .step("h1")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
                modes={
                    InstructionMode.create(
                        mode=AddressingMode.ABSOLUTE,
                        opcode=Byte(0x00),
                        impls={
                            InstructionImpl.create(
                                steps=[
                                    Step.create({"h1"}),
                                    Step.create({"c1"}),
                                ],
                            ),
                        },
                    ),
                },
            )
        }
    )
