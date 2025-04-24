from pytest_subtests import SubTests

from flip.bytes import Byte
from flip.components.controller import Assembler
from flip.instructions import (
    AddressingMode,
    Instruction,
    InstructionImpl,
    InstructionMode,
    InstructionSet,
    Step,
)


def test_assemble(subtests: SubTests) -> None:
    instruction_set = InstructionSet.create().with_instruction(
        Instruction.create(
            name="i",
        )
        .with_mode(
            InstructionMode.create(
                mode=AddressingMode.IMMEDIATE,
                opcode=Byte(1),
                impls={
                    InstructionImpl.create(
                        statuses={"s1": False},
                        steps=[
                            Step.create(controls={"c1", "c2"}),
                            Step.create(controls={"c2", "c3"}),
                        ],
                    ),
                    InstructionImpl.create(
                        statuses={"s1": True},
                        steps=[
                            Step.create(controls={"c3", "c4"}),
                            Step.create(controls={"c4", "c5"}),
                        ],
                    ),
                },
            ),
        )
        .with_mode(
            InstructionMode.create(
                mode=AddressingMode.IMMEDIATE,
                opcode=Byte(2),
                impls={
                    InstructionImpl.create(
                        statuses={},  # don't care about s1
                        steps=[
                            Step.create(controls={"c6"}),
                        ],
                    ),
                },
            ),
        )
    )
    assembler = Assembler(instruction_set)
    instruction_memory = assembler.assemble()
    for opcode, statuses, step_index, controls in list[
        tuple[
            Byte,
            dict[str, bool],
            Byte,
            set[str],
        ]
    ](
        [
            (
                Byte(1),
                {
                    "s1": False,
                },
                Byte(0),
                {"c1", "c2"},
            ),
            (
                Byte(1),
                {
                    "s1": True,
                },
                Byte(0),
                {"c3", "c4"},
            ),
            (
                Byte(1),
                {
                    "s1": True,
                },
                Byte(1),
                {"c4", "c5"},
            ),
            (
                Byte(2),
                {"s1": False},
                Byte(0),
                {"c6"},
            ),
            (
                Byte(2),
                {"s1": True},
                Byte(0),
                {"c6"},
            ),
        ]
    ):
        with subtests.test(
            opcode=opcode, statuses=statuses, step_index=step_index, controls=controls
        ):
            assert (
                instruction_memory.get(
                    opcode=opcode,
                    statuses=statuses,
                    step_index=step_index,
                )
                == controls
            )
