from flip.bytes import Byte
from flip.components.controller import Instruction, InstructionSet, Step


def test_get_controls() -> None:
    assert InstructionSet.create(
        instructions={
            Instruction.create(
                opcode=Byte(0),
                statuses={},
                steps=[
                    Step.create(controls={"c1", "c2"}),
                    Step.create(controls={"c2", "c3"}),
                ],
            ),
            Instruction.create(
                opcode=Byte(1),
                statuses={},
                steps=[
                    Step.create(controls={"c3", "c4"}),
                    Step.create(controls={"c4", "c5"}),
                ],
            ),
        }
    ).controls == {"c1", "c2", "c3", "c4", "c5"}


def test_get_statuses() -> None:
    assert InstructionSet.create(
        instructions={
            Instruction.create(
                opcode=Byte(0),
                statuses={"s1": False, "s2": True},
                steps=[
                    Step.create(controls={"c1", "c2"}),
                    Step.create(controls={"c2", "c3"}),
                ],
            ),
            Instruction.create(
                opcode=Byte(1),
                statuses={"s2": False, "s3": True},
                steps=[
                    Step.create(controls={"c3", "c4"}),
                    Step.create(controls={"c4", "c5"}),
                ],
            ),
        }
    ).statuses == {"s1", "s2", "s3"}
