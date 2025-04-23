from dataclasses import dataclass, replace
from typing import Iterable, Iterator, Optional, Sized, override

from flip.instructions.instruction_mode import InstructionMode


@dataclass(frozen=True)
class Instruction(Sized, Iterable[InstructionMode]):
    name: str
    _modes: frozenset[InstructionMode]

    @classmethod
    def create(
        cls,
        name: str,
        modes: Optional[Iterable[InstructionMode]] = None,
    ) -> "Instruction":
        return cls(
            name=name, _modes=frozenset(modes) if modes is not None else frozenset()
        )

    @override
    def __len__(self) -> int:
        return len(self._modes)

    @override
    def __iter__(self) -> Iterator[InstructionMode]:
        return iter(self._modes)

    def _with_modes(self, modes: Iterable[InstructionMode]) -> "Instruction":
        return replace(self, _modes=frozenset(modes))

    def with_modes(self, modes: Iterable[InstructionMode]) -> "Instruction":
        return self._with_modes(self._modes | frozenset(modes))

    def with_mode(self, mode: InstructionMode) -> "Instruction":
        return self._with_modes(self._modes | {mode})
