from pytest_subtests import SubTests

from flip.bytes import Byte
from flip.components.controller import (
    Assembler,
    Instruction,
    InstructionSet,
    Step,
)


def test_assemble(subtests: SubTests) -> None:
    instruction_set = InstructionSet.create(
        instructions={
            Instruction.create(
                name="i1",
                opcode=Byte(0),
                statuses={"s1": False, "s2": True},
                steps=[
                    Step.create(controls={"c1", "c2"}),
                    Step.create(controls={"c2", "c3"}),
                ],
            ),
            Instruction.create(
                name="i2",
                opcode=Byte(1),
                statuses={"s2": True, "s3": False},
                steps=[
                    Step.create(controls={"c3", "c4"}),
                    Step.create(controls={"c4", "c5"}),
                ],
            ),
        }
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
                Byte(0),
                {
                    "s1": False,
                    "s2": True,
                    "s3": False,
                },
                Byte(0),
                {"c1", "c2"},
            ),
            (
                Byte(0),
                {
                    "s1": False,
                    "s2": True,
                    "s3": True,
                },
                Byte(0),
                {"c1", "c2"},
            ),
            (
                Byte(1),
                {
                    "s1": False,
                    "s2": True,
                    "s3": False,
                },
                Byte(1),
                {"c4", "c5"},
            ),
        ]
    ):
        with subtests.test(
            opcode=opcode, statuses=statuses, step_index=step_index, controls=controls
        ):
            assert (
                instruction_memory.get(
                    opcode=opcode, statuses=statuses, step_index=step_index
                )
                == controls
            )
