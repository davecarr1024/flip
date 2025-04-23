from dataclasses import dataclass, replace
from typing import Iterable, Iterator, Optional, Sized, override

from flip.bytes import Byte
from flip.instructions.addressing_mode import AddressingMode
from flip.instructions.instruction_impl import InstructionImpl
from flip.instructions.step import Step


@dataclass(frozen=True)
class InstructionMode(Sized, Iterable[InstructionImpl]):
    mode: AddressingMode
    opcode: Byte
    _impls: frozenset[InstructionImpl]

    @override
    def __len__(self) -> int:
        return len(self._impls)

    @override
    def __iter__(self) -> Iterator[InstructionImpl]:
        return iter(self._impls)

    @classmethod
    def create(
        cls,
        mode: AddressingMode,
        opcode: Byte,
        impls: Optional[Iterable[InstructionImpl]] = None,
    ) -> "InstructionMode":
        return cls(
            mode=mode,
            opcode=opcode,
            _impls=(frozenset(impls) if impls is not None else frozenset()),
        )

    def _with_impls(self, impls: Iterable[InstructionImpl]) -> "InstructionMode":
        return replace(self, _impls=frozenset(impls))

    def with_impls(self, impls: Iterable[InstructionImpl]) -> "InstructionMode":
        return self._with_impls(self._impls | frozenset(impls))

    def with_impl(self, impl: InstructionImpl) -> "InstructionMode":
        return self._with_impls(self._impls | {impl})

    def with_header(self, steps: Iterable[Step]) -> "InstructionMode":
        return self._with_impls(impl.with_header(steps) for impl in self._impls)

    def with_footer(self, steps: Iterable[Step]) -> "InstructionMode":
        return self._with_impls(impl.with_footer(steps) for impl in self._impls)

    @property
    def controls(self) -> frozenset[str]:
        """The set of all controls used by any impl of this mode."""
        return frozenset[str]().union(*[impl.controls for impl in self])

    @property
    def statuses(self) -> frozenset[str]:
        """The set of all statuses used by any impl of this mode."""
        return frozenset[str]().union(*[impl.statuses.keys() for impl in self])
