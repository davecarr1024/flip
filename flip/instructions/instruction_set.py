from dataclasses import dataclass, field, replace
from typing import Iterable, Iterator, Mapping, Optional, Sized, override

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

    @staticmethod
    def _normalize_step(step: Step | list[str] | str) -> Step:
        match step:
            case Step():
                return step
            case list():
                return Step.create(controls=step)
            case str():
                return Step.create(controls=[step])

    @staticmethod
    def _normalize_steps(steps: Iterable[Step | list[str] | str]) -> list[Step]:
        return list(map(InstructionSet._normalize_step, steps))

    def with_header(self, *steps: Step | list[str] | str) -> "InstructionSet":
        return self._with_instructions(
            instruction.with_header(self._normalize_steps(steps))
            for instruction in self._instructions
        )

    def with_footer(self, *steps: Step | list[str] | str) -> "InstructionSet":
        return self._with_instructions(
            instruction.with_footer(self._normalize_steps(steps))
            for instruction in self._instructions
        )

    @property
    def controls(self) -> frozenset[str]:
        """The set of all controls used by any instruction in the set."""
        return frozenset[str]().union(*[instruction.controls for instruction in self])

    @property
    def statuses(self) -> frozenset[str]:
        """The set of all statuses used by any instruction in the set."""
        return frozenset[str]().union(*[instruction.statuses for instruction in self])

    @property
    def max_num_steps(self) -> int:
        """The maximum number of steps in any instruction in the set."""
        return max(instruction.max_num_steps for instruction in self)

    @staticmethod
    def builder() -> "instruction_set_builder.InstructionSetBuilder":
        return instruction_set_builder.InstructionSetBuilder()

    @property
    def instructions_by_name(self) -> Mapping[str, Instruction]:
        return {instruction.name: instruction for instruction in self._instructions}


from flip.instructions import instruction_set_builder
