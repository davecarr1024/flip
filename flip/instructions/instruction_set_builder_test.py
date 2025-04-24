from typing import Literal

import pytest
from pytest_subtests import SubTests

from flip.bytes import Byte
from flip.instructions import (
    AddressingMode,
    Instruction,
    InstructionImpl,
    InstructionMode,
    InstructionSet,
    InstructionSetBuilder,
    Step,
)


def test_instruction() -> None:
    assert InstructionSet.builder().instruction("i").build() == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
            )
        }
    )


def test_mode(subtests: SubTests) -> None:
    for opcode, expected_opcode in list[tuple[Byte | int, Byte]](
        [(Byte(0x00), Byte(0x00)), (0x00, Byte(0x00))]
    ):
        for mode, expected_mode in list[
            tuple[
                AddressingMode
                | Literal[
                    "none",
                    "immediate",
                    "relative",
                    "zero_page",
                    "absolute",
                ],
                AddressingMode,
            ]
        ](
            [
                (AddressingMode.NONE, AddressingMode.NONE),
                ("none", AddressingMode.NONE),
                ("immediate", AddressingMode.IMMEDIATE),
                ("relative", AddressingMode.RELATIVE),
                ("zero_page", AddressingMode.ZERO_PAGE),
                ("absolute", AddressingMode.ABSOLUTE),
            ]
        ):
            with subtests.test(opcode=opcode, mode=mode):
                assert InstructionSet.builder().instruction("i").mode(
                    mode,
                    opcode,
                ).build() == InstructionSet.create(
                    instructions={
                        Instruction.create(
                            name="i",
                        ).with_mode(
                            InstructionMode.create(
                                mode=expected_mode,
                                opcode=expected_opcode,
                            )
                        )
                    }
                )


def test_impl_empty() -> None:
    assert (
        InstructionSet.builder().instruction("i").mode("none", 0x00).impl().build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
            ).with_mode(
                InstructionMode.create(
                    mode=AddressingMode.NONE,
                    opcode=Byte(0x00),
                ).with_impl(InstructionImpl.create())
            )
        }
    )


def test_impl_with_statuses() -> None:
    assert (
        InstructionSet.builder()
        .instruction("i")
        .mode("none", 0x00)
        .impl(a=True, b=False)
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
            ).with_mode(
                InstructionMode.create(
                    mode=AddressingMode.NONE,
                    opcode=Byte(0x00),
                ).with_impl(
                    InstructionImpl.create(
                        statuses={"a": True, "b": False},
                    )
                )
            )
        }
    )


def test_step_no_impl() -> None:
    assert (
        InstructionSet.builder()
        .instruction("i")
        .mode("none", 0x00)
        .step("c1", "c2")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
            ).with_mode(
                InstructionMode.create(
                    mode=AddressingMode.NONE,
                    opcode=Byte(0x00),
                ).with_impl(
                    InstructionImpl.create(
                        steps=[
                            Step.create(controls={"c1", "c2"}),
                        ]
                    )
                )
            )
        }
    )


def test_step_with_impl_with_statuses() -> None:
    assert (
        InstructionSet.builder()
        .instruction("i")
        .mode("none", 0x00)
        .impl(a=True, b=False)
        .step("c1", "c2")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
            ).with_mode(
                InstructionMode.create(
                    mode=AddressingMode.NONE,
                    opcode=Byte(0x00),
                ).with_impl(
                    InstructionImpl.create(
                        statuses={"a": True, "b": False},
                        steps=[
                            Step.create(controls={"c1", "c2"}),
                        ],
                    )
                )
            )
        }
    )


def test_two_instructions() -> None:
    assert (
        InstructionSet.builder().instruction("i1").instruction("i2").build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i1",
            ),
            Instruction.create(
                name="i2",
            ),
        }
    )


def test_two_modes() -> None:
    assert (
        InstructionSet.builder()
        .instruction("i")
        .mode("none", 0x00)
        .mode("immediate", 0x01)
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
            )
            .with_mode(
                InstructionMode.create(
                    mode=AddressingMode.NONE,
                    opcode=Byte(0x00),
                )
            )
            .with_mode(
                InstructionMode.create(
                    mode=AddressingMode.IMMEDIATE,
                    opcode=Byte(0x01),
                )
            )
        }
    )


def test_two_impls() -> None:
    assert (
        InstructionSet.builder()
        .instruction("i")
        .mode("none", 0x00)
        .impl(a=True)
        .impl(a=False)
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
            ).with_mode(
                InstructionMode.create(
                    mode=AddressingMode.NONE,
                    opcode=Byte(0x00),
                    impls={
                        InstructionImpl.create(statuses={"a": True}),
                        InstructionImpl.create(statuses={"a": False}),
                    },
                )
            )
        }
    )


def test_two_steps() -> None:
    assert (
        InstructionSet.builder()
        .instruction("i")
        .mode("none", 0x00)
        .step("c1", "c2")
        .step("c3", "c4")
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
            ).with_mode(
                InstructionMode.create(
                    mode=AddressingMode.NONE,
                    opcode=Byte(0x00),
                ).with_impl(
                    InstructionImpl.create(
                        steps=[
                            Step.create(controls={"c1", "c2"}),
                            Step.create(controls={"c3", "c4"}),
                        ],
                    )
                )
            )
        }
    )


def test_mode_without_instruction_raises() -> None:
    # Can't define a mode before an instruction
    builder = InstructionSetBuilder()
    with pytest.raises(InstructionSetBuilder.ValueError):
        builder.mode("none", 0x00)


def test_impl_without_mode_raises() -> None:
    # Can't define an impl without first defining a mode
    builder = InstructionSetBuilder().instruction("i")
    with pytest.raises(InstructionSetBuilder.ValueError):
        builder.impl(a=True)


def test_step_without_mode_raises() -> None:
    # Can't define a step without a mode (and implicitly an impl)
    builder = InstructionSetBuilder().instruction("i")
    with pytest.raises(InstructionSetBuilder.ValueError):
        builder.step("c1")


def test_header() -> None:
    assert (
        InstructionSet.builder()
        .instruction("i", 0x00)
        .step("c1")
        .header("c2", ["c3", "c4"])
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
            ).with_mode(
                InstructionMode.create(
                    mode=AddressingMode.NONE,
                    opcode=Byte(0x00),
                ).with_impl(
                    InstructionImpl.create(
                        steps=[
                            Step.create(controls={"c2"}),
                            Step.create(controls={"c3", "c4"}),
                            Step.create(controls={"c1"}),
                        ],
                    )
                )
            )
        }
    )


def test_footer() -> None:
    assert (
        InstructionSet.builder()
        .instruction("i", 0x00)
        .step("c1")
        .footer("c2", ["c3", "c4"])
        .build()
    ) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i",
            ).with_mode(
                InstructionMode.create(
                    mode=AddressingMode.NONE,
                    opcode=Byte(0x00),
                ).with_impl(
                    InstructionImpl.create(
                        steps=[
                            Step.create(controls={"c1"}),
                            Step.create(controls={"c2"}),
                            Step.create(controls={"c3", "c4"}),
                        ],
                    )
                )
            )
        }
    )
