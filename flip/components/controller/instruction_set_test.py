from flip.bytes import Byte
from flip.components.controller import Instruction, InstructionSet, Step

is_ = InstructionSet.create(
    instructions={
        Instruction.create(
            name="i1",
            opcode=Byte(0),
            statuses={"s1": True, "s2": False},
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


def test_get_controls() -> None:
    assert is_.controls == {"c1", "c2", "c3", "c4", "c5"}


def test_get_statuses() -> None:
    assert is_.statuses == {"s1", "s2", "s3"}


def test_with_header() -> None:
    assert is_.with_header([Step.create(controls={"c6"})]) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i1",
                opcode=Byte(0),
                statuses={"s1": True, "s2": False},
                steps=[
                    Step.create(controls={"c6"}),
                    Step.create(controls={"c1", "c2"}),
                    Step.create(controls={"c2", "c3"}),
                ],
            ),
            Instruction.create(
                name="i2",
                opcode=Byte(1),
                statuses={"s2": True, "s3": False},
                steps=[
                    Step.create(controls={"c6"}),
                    Step.create(controls={"c3", "c4"}),
                    Step.create(controls={"c4", "c5"}),
                ],
            ),
        }
    )


def test_with_footer() -> None:
    assert is_.with_footer([Step.create(controls={"c6"})]) == InstructionSet.create(
        instructions={
            Instruction.create(
                name="i1",
                opcode=Byte(0),
                statuses={"s1": True, "s2": False},
                steps=[
                    Step.create(controls={"c1", "c2"}),
                    Step.create(controls={"c2", "c3"}),
                    Step.create(controls={"c6"}),
                ],
            ),
            Instruction.create(
                name="i2",
                opcode=Byte(1),
                statuses={"s2": True, "s3": False},
                steps=[
                    Step.create(controls={"c3", "c4"}),
                    Step.create(controls={"c4", "c5"}),
                    Step.create(controls={"c6"}),
                ],
            ),
        }
    )
