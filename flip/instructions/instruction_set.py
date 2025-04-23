from dataclasses import dataclass, field, replace
from typing import Iterable, Iterator, Optional, Sized, override

from flip.instructions.instruction import Instruction
from flip.instructions.step import Step


@dataclass(frozen=True)
class InstructionSet(Sized, Iterable[Instruction]):
    _instructions: frozenset[Instruction] = field(
        default_factory=frozenset[Instruction]
    )

    @override
    def __len__(self) -> int:
        return len(self._instructions)

    @override
    def __iter__(self) -> Iterator[Instruction]:
        return iter(self._instructions)

    @classmethod
    def create(
        cls,
        instructions: Optional[Iterable[Instruction]] = None,
    ) -> "InstructionSet":
        return cls(
            _instructions=(
                frozenset(instructions) if instructions is not None else frozenset()
            )
        )

    def _with_instructions(
        self, instructions: Iterable[Instruction]
    ) -> "InstructionSet":
        return replace(self, _instructions=frozenset(instructions))

    def with_instructions(
        self, instructions: Iterable[Instruction]
    ) -> "InstructionSet":
        return self._with_instructions(self._instructions | frozenset(instructions))

    def with_instruction(self, instruction: Instruction) -> "InstructionSet":
        return self._with_instructions(self._instructions | {instruction})

    def with_header(self, steps: Iterable[Step]) -> "InstructionSet":
        return self._with_instructions(
            instruction.with_header(steps) for instruction in self._instructions
        )

    def with_footer(self, steps: Iterable[Step]) -> "InstructionSet":
        return self._with_instructions(
            instruction.with_footer(steps) for instruction in self._instructions
        )

    @property
    def controls(self) -> frozenset[str]:
        """The set of all controls used by any instruction in the set."""
        return frozenset[str]().union(*[instruction.controls for instruction in self])

    @property
    def statuses(self) -> frozenset[str]:
        """The set of all statuses used by any instruction in the set."""
        return frozenset[str]().union(*[instruction.statuses for instruction in self])
