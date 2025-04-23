from dataclasses import dataclass
from typing import Iterable

from flip.components.controller.instruction import Instruction


@dataclass(frozen=True)
class InstructionSet:
    instructions: frozenset[Instruction]

    @classmethod
    def create(cls, instructions: Iterable[Instruction]) -> "InstructionSet":
        return cls(instructions=frozenset(instructions))

    @property
    def controls(self) -> frozenset[str]:
        """The set of all controls used by any instruction in the instruction set."""
        return frozenset[str]().union(
            *[instruction.controls for instruction in self.instructions]
        )

    @property
    def statuses(self) -> frozenset[str]:
        """The set of all statuses used by any instruction in the instruction set."""
        return frozenset[str]().union(
            *[
                frozenset(instruction.statuses.keys())
                for instruction in self.instructions
            ]
        )
