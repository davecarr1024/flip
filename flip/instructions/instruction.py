from dataclasses import dataclass, field, replace
from typing import Iterable, Iterator, Mapping, Optional, Sized, override

from flip.bytes import Byte
from flip.instructions.addressing_mode import AddressingMode
from flip.instructions.instruction_impl import InstructionImpl
from flip.instructions.instruction_mode import InstructionMode
from flip.instructions.step import Step


@dataclass(frozen=True)
class Instruction(Sized, Iterable[InstructionMode]):
    name: str
    _modes: frozenset[InstructionMode] = field(
        default_factory=frozenset[InstructionMode]
    )

    @classmethod
    def create(
        cls,
        name: str,
        modes: Optional[Iterable[InstructionMode]] = None,
    ) -> "Instruction":
        return cls(
            name=name, _modes=frozenset(modes) if modes is not None else frozenset()
        )

    @classmethod
    def create_simple(
        cls,
        name: str,
        mode: AddressingMode,
        opcode: Byte,
        steps: Iterable[Step],
    ) -> "Instruction":
        return cls(name=name).with_mode(
            InstructionMode.create(mode=mode, opcode=opcode).with_impl(
                InstructionImpl.create(steps=steps)
            )
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

    def with_header(self, steps: Iterable[Step]) -> "Instruction":
        return self._with_modes(mode.with_header(steps) for mode in self._modes)

    def with_footer(self, steps: Iterable[Step]) -> "Instruction":
        return self._with_modes(mode.with_footer(steps) for mode in self._modes)

    @property
    def controls(self) -> frozenset[str]:
        """The set of all controls used by any mode of this instruction."""
        return frozenset[str]().union(*[mode.controls for mode in self])

    @property
    def statuses(self) -> frozenset[str]:
        """The set of all statuses used by any mode of this instruction."""
        return frozenset[str]().union(*[mode.statuses for mode in self])

    @property
    def max_num_steps(self) -> int:
        return max(mode.max_num_steps for mode in self)

    @property
    def modes_by_addressing_mode(self) -> Mapping[AddressingMode, InstructionMode]:
        return {mode.mode: mode for mode in self._modes}
