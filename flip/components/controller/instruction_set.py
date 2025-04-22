from collections import defaultdict
from dataclasses import dataclass
from typing import Iterator, Mapping, Set, override

from flip.bytes import Byte
from flip.components.controller.instruction import Instruction


@dataclass(frozen=True)
class InstructionSet(Set[Instruction]):
    instructions: frozenset[Instruction]

    @override
    def __len__(self) -> int:
        return len(self.instructions)

    @override
    def __iter__(self) -> Iterator[Instruction]:
        yield from self.instructions

    @override
    def __contains__(self, instruction: object) -> bool:
        return instruction in self.instructions

    @property
    def instructions_by_opcode(self) -> Mapping[Byte, frozenset[Instruction]]:
        instructions = defaultdict[Byte, set[Instruction]](set)
        for instruction in self.instructions:
            instructions[instruction.opcode].add(instruction)
        return {
            opcode: frozenset(instructions)
            for opcode, instructions in instructions.items()
        }

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
